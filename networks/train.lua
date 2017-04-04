require 'torch'
require 'nn'
require 'optim'

require 'LanguageModel'
require 'util.DataLoader'

local utils = require 'util.utils'
local unpack = unpack or table.unpack

local cmd = torch.CmdLine()

-- Dataset options
cmd:option('-input_h5', 'my_data.h5')
cmd:option('-input_json', 'my_data.json')
cmd:option('-batch_size', 50)
cmd:option('-seq_length', 50)

-- Model options
cmd:option('-init_from', '')
cmd:option('-model_type', 'rnn')
cmd:option('-wordvec_size', 64)
cmd:option('-rnn_size', 32)
cmd:option('-num_layers', 2)
cmd:option('-dropout', 0)
cmd:option('-batchnorm', 1)

-- Optimization options
cmd:option('-max_epochs', 50)
cmd:option('-early_stopping', 1)
cmd:option('-grad_method', 'adam')
cmd:option('-learning_rate', 2e-3)
cmd:option('-grad_clip', 5)
cmd:option('-lr_decay_every', 5)
cmd:option('-lr_decay_factor', 0.5)

-- Output options
cmd:option('-print_every', 1)
cmd:option('-checkpoint_every', 1000)
cmd:option('-checkpoint_name', 'cv/test/test')
cmd:option('-init_checkpoint', 0)

-- Benchmark options
cmd:option('-speed_benchmark', 0)
cmd:option('-memory_benchmark', 0)

-- Backend options
cmd:option('-gpu', -1)
cmd:option('-gpu_backend', 'cuda')

local opt = cmd:parse(arg)


-- Set up GPU stuff
local dtype = 'torch.FloatTensor'
if opt.gpu >= 0 and opt.gpu_backend == 'cuda' then
  require 'cutorch'
  require 'cunn'
  cutorch.setDevice(opt.gpu + 1)
  dtype = 'torch.CudaTensor'
  print(string.format('Running with CUDA on GPU %d', opt.gpu))
elseif opt.gpu >= 0 and opt.gpu_backend == 'opencl' then
  -- Memory benchmarking is only supported in CUDA mode
  -- TODO: Time benchmarking is probably wrong in OpenCL mode.
  require 'cltorch'
  require 'clnn'
  cltorch.setDevice(opt.gpu + 1)
  dtype = torch.Tensor():cl():type()
  print(string.format('Running with OpenCL on GPU %d', opt.gpu))
else
  -- Memory benchmarking is only supported in CUDA mode
  opt.memory_benchmark = 0
  print 'Running in CPU mode'
end


-- Initialize the DataLoader and vocabulary
local loader = DataLoader(opt)
local vocab = utils.read_json(opt.input_json)
local idx_to_token = {}
for k, v in pairs(vocab.idx_to_token) do
  idx_to_token[tonumber(k)] = v
end

-- Initialize the model and criterion
local opt_clone = torch.deserialize(torch.serialize(opt))
opt_clone.idx_to_token = idx_to_token
local model = nil
if opt.init_from ~= '' then
  print('Initializing from ', opt.init_from)
  model = torch.load(opt.init_from).model:type(dtype)
else
  model = nn.LanguageModel(opt_clone):type(dtype)
end
local params, grad_params = model:getParameters()
local crit = nn.CrossEntropyCriterion():type(dtype)

-- Compute the number of parameters of the network
local n_parameters = tostring(params:size(1)) 
print('Number of parameters: ', params:size())

-- Set up some variables we will use below
local N, T = opt.batch_size, opt.seq_length
local train_loss_history = {}
local val_loss_history = {}
local val_loss_history_it = {}
local forward_backward_times = {}
local init_memory_usage, memory_usage = nil, {}

if opt.memory_benchmark == 1 then
  -- This should only be enabled in GPU mode
  assert(cutorch)
  cutorch.synchronize()
  local free, total = cutorch.getMemoryUsage(cutorch.getDevice())
  init_memory_usage = total - free
end

-- Loss function that we pass to an optim method
local function f(w)
  assert(w == params)
  grad_params:zero()

  -- Get a minibatch and run the model forward, maybe timing it
  local timer
  local x, y = loader:nextBatch('train')
  x, y = x:type(dtype), y:type(dtype)
  if opt.speed_benchmark == 1 then
    if cutorch then cutorch.synchronize() end
    timer = torch.Timer()
  end
  local scores = model:forward(x)

  -- Use the Criterion to compute loss; we need to reshape the scores to be
  -- two-dimensional before doing so. Annoying.
  local scores_view = scores:view(N * T, -1)
  local y_view = y:view(N * T)
  local loss = crit:forward(scores_view, y_view)

  -- Run the Criterion and model backward to compute gradients, maybe timing it
  local grad_scores = crit:backward(scores_view, y_view):view(N, T, -1)
  model:backward(x, grad_scores)
  if timer then
    if cutorch then cutorch.synchronize() end
    local time = timer:time().real
    print('Forward / Backward pass took ', time)
    table.insert(forward_backward_times, time)
  end

  -- Maybe record memory usage
  if opt.memory_benchmark == 1 then
    assert(cutorch)
    if cutorch then cutorch.synchronize() end
    local free, total = cutorch.getMemoryUsage(cutorch.getDevice())
    local memory_used = total - free - init_memory_usage
    local memory_used_mb = memory_used / 1024 / 1024
    print(string.format('Using %dMB of memory', memory_used_mb))
    table.insert(memory_usage, memory_used)
  end

  if opt.grad_clip > 0 then
    grad_params:clamp(-opt.grad_clip, opt.grad_clip)
  end

  return loss, grad_params
end

-- Train the model!
local optim_config
if opt.grad_method == 'adam' then
  optim_config = {learningRate = opt.learning_rate}
end
local num_train = loader.split_sizes['train']
local num_iterations = opt.max_epochs * num_train
model:training()
for i = 1, num_iterations do
  local epoch = math.floor(i / num_train) + 1

  --save a checkpoint of the yet to be train network
  if i == 1 and opt.init_checkpoint == 1 then
    -- First save a JSON checkpoint, excluding the model
    local checkpoint = {
      opt = opt,
      train_loss_history = train_loss_history,
      val_loss_history = val_loss_history,
      val_loss_history_it = val_loss_history_it,
      forward_backward_times = forward_backward_times,
      memory_usage = memory_usage,
    }
    local filename = string.format('%s_%d.json', opt.checkpoint_name, i)
    -- Make sure the output directory exists before we try to write it
    paths.mkdir(paths.dirname(filename))
    utils.write_json(filename, checkpoint)

    -- Now save a torch checkpoint with the model
    -- Cast the model to float before saving so it can be used on CPU
    model:clearState()
    model:float()
    checkpoint.model = model
    local filename = string.format('%s_%d.t7', opt.checkpoint_name, i)
    paths.mkdir(paths.dirname(filename))
    torch.save(filename, checkpoint)
    model:type(dtype)
    params, grad_params = model:getParameters()
    collectgarbage()
  end


  -- Check if we are at the end of an epoch
  if i % num_train == 0 then
    model:resetStates() -- Reset hidden states

    -- Maybe decay learning rate
    if opt.grad_method == 'adam' and epoch % opt.lr_decay_every == 0 then
      local old_lr = optim_config.learningRate
      optim_config = {learningRate = old_lr * opt.lr_decay_factor}
    end
  end

  -- Take a gradient step and maybe print
  -- Note that adam returns a singleton array of losses
  local _, loss
  if opt.grad_method == 'adam' then
    _, loss = optim.adam(f, params, optim_config)
  end
  table.insert(train_loss_history, loss[1])
  if opt.print_every > 0 and i % opt.print_every == 0 then
    local float_epoch = i / num_train + 1
    local msg = 'Epoch %.2f / %d, i = %d / %d, loss = %f'
    local args = {msg, float_epoch, opt.max_epochs, i, num_iterations, loss[1]}
    print(string.format(unpack(args)))
  end

  -- Maybe save a checkpoint
  local check_every = opt.checkpoint_every
  if i % num_train == 0 then
    -- Evaluate loss on the validation set. Note that we reset the state of
    -- the model; this might happen in the middle of an epoch, but that
    -- shouldn't cause too much trouble.
    -- FIX: doesn't happen in the middle of an epoch but check_every 
    -- isn't used anymore
    model:evaluate()
    model:resetStates()
    local num_val = loader.split_sizes['val']
    local val_loss = 0
    for j = 1, num_val do
      local xv, yv = loader:nextBatch('val')
      xv = xv:type(dtype)
      yv = yv:type(dtype):view(N * T)
      local scores = model:forward(xv):view(N * T, -1)
      val_loss = val_loss + crit:forward(scores, yv)
    end
    val_loss = val_loss / num_val
    print('val_loss = ', val_loss)
    table.insert(val_loss_history, val_loss)
    table.insert(val_loss_history_it, i)
    model:resetStates()
    model:training()

    if opt.early_stopping == 1 then
      --if the validation loss isn't decreasing anymore, then we should stop
      --the training and only keep the best checkpoint
      if #val_loss_history >= 3 then --we only want to keep the best network
        os.remove(string.format('%s_%d.json', opt.checkpoint_name, val_loss_history_it[#val_loss_history-2]))
        os.remove(string.format('%s_%d.t7', opt.checkpoint_name, val_loss_history_it[#val_loss_history-2]))
      end
      if #val_loss_history >= 2 then
        local new_loss = val_loss_history[#val_loss_history]
        local old_loss = val_loss_history[#val_loss_history-1]
        if new_loss > old_loss or math.abs(old_loss - new_loss) < 0.001 then
          --stop the training
          break
        end
      end
    end


    -- First save a JSON checkpoint, excluding the model
    local checkpoint = {
      opt = opt,
      train_loss_history = train_loss_history,
      val_loss_history = val_loss_history,
      val_loss_history_it = val_loss_history_it,
      forward_backward_times = forward_backward_times,
      memory_usage = memory_usage,
      n_parameters = n_parameters,
      loss = val_loss_history[#val_loss_history]
    }
    local filename = string.format('%s_%d.json', opt.checkpoint_name, i)
    -- Make sure the output directory exists before we try to write it
    paths.mkdir(paths.dirname(filename))
    utils.write_json(filename, checkpoint)

    -- Now save a torch checkpoint with the model
    -- Cast the model to float before saving so it can be used on CPU
    model:clearState()
    model:float()
    checkpoint.model = model
    local filename = string.format('%s_%d.t7', opt.checkpoint_name, i)
    paths.mkdir(paths.dirname(filename))
    torch.save(filename, checkpoint)
    model:type(dtype)
    params, grad_params = model:getParameters()
    collectgarbage()
  end
end
