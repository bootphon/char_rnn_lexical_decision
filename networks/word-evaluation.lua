require 'torch'
require 'nn'

require 'LanguageModel'

local cmd = torch.CmdLine()
cmd:option('-checkpoint', 'cv/test/test_7168.t7')
cmd:option('-length', 1)
cmd:option('-start_text', '')
cmd:option('-sample', 1)
cmd:option('-temperature', 1)
cmd:option('-gpu', -1)
cmd:option('-gpu_backend', 'cuda')
cmd:option('-verbose', 0)
cmd:option('-stimuli', '../data/stimuli.txt')
cmd:option('-output_path', '../probs/corpus100k/')
local opt = cmd:parse(arg)


local checkpoint = torch.load(opt.checkpoint)
local model = checkpoint.model

local msg
if opt.gpu >= 0 and opt.gpu_backend == 'cuda' then
  require 'cutorch'
  require 'cunn'
  cutorch.setDevice(opt.gpu + 1)
  model:cuda()
  msg = string.format('Running with CUDA on GPU %d', opt.gpu)
elseif opt.gpu >= 0 and opt.gpu_backend == 'opencl' then
  require 'cltorch'
  require 'clnn'
  model:cl()
  msg = string.format('Running with OpenCL on GPU %d', opt.gpu)
else
  msg = 'Running in CPU mode'
end
if opt.verbose == 1 then print(msg) end

model:evaluate()

local stimuli = opt.stimuli
local name = string.match(opt.checkpoint, '([a-z0-9_]+)_%d+.t7')
print(name)
local output = opt.output_path:gsub('/$','')..'/'..name..'.txt'

-- extract words and nonwords from the stimuli file
local word_list = {}
local nonword_list = {}
local first_line = true

local file = io.open(stimuli,'r')
for line in io.lines(stimuli) do
  if first_line then
    first_line = false
  else
    word_list[#word_list + 1] = line:match("%w+")
    nonword_list[#nonword_list + 1] = line:match("%s(%w+)")
  end
end
io.close(file)


print('Computing word probabilities...')

local word_probs = {}
for i=1,#word_list do
  word = word_list[i]
  local probability = model:getProb(opt,word)
  word_probs[#word_probs + 1] = probability
end

print('Computing nonword probabilities...')

local nonword_probs = {}
for i=1,#nonword_list do
  word = nonword_list[i]
  local probability = model:getProb(opt,word)
  nonword_probs[#nonword_probs + 1] = probability
end

print('Writing the results to '..output)

paths.mkdir(paths.dirname(output)) -- Make sure the output directory exists before we try to write it
local output_file = io.open(output, 'w')
local columns = 'Word\tMatch\tWord_Prob\tNonword_Prob'
output_file:write(columns)
for i=1,#word_list do
  local line = word_list[i]..'\t'..nonword_list[i]..'\t'..word_probs[i]..'\t'..nonword_probs[i]
  output_file:write('\n'..line)
end
io.close(output_file)
