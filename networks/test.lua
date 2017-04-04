require 'torch'
require 'nn'

require 'LanguageModel'



local N, T, D, H, V = 2, 3, 4, 5, 6
local idx_to_token = {[1]='a', [2]='b', [3]='c', [4]='d', [5]='e', [6]='f'}
local LM = nn.LanguageModel{
  idx_to_token=idx_to_token,
  model_type='rnn',
  wordvec_size=D,
  rnn_size=H,
  num_layers=6,
  dropout=0,
  batchnorm=0,
}

local TT = 100
local start_text = 'bad'
local sampled = LM:sample{start_text=start_text, length=TT}
print(sampled)


--[[
function tests.encodeDecodeTest()
  local idx_to_token = {
    [1]='a', [2]='b', [3]='c', [4]='d',
    [5]='e', [6]='f', [7]='g', [8]=' ',
  }
  local N, T, D, H, V = 2, 3, 4, 5, 7
  local LM = nn.LanguageModel{
    idx_to_token=idx_to_token,
    model_type='rnn',
    wordvec_size=D,
    rnn_size=H,
    num_layers=6,
    dropout=0,
    batchnorm=0,
  }

  local s = 'a bad feed'
  local encoded = LM:encode_string(s)
  local expected_encoded = torch.LongTensor{1, 8, 2, 1, 4, 8, 6, 5, 5, 4}
  tester:assert(torch.all(torch.eq(encoded, expected_encoded)))

  local s2 = LM:decode_string(encoded)
  tester:assert(s == s2)
end
]]

