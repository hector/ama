clear all
close all
addpath('../MATLAB-Chroma-Toolbox_2.0')

for i=1:96
  filename = sprintf('%02d.wav', i);
  [f_audio,sideinfo] = wav_to_audio('', '../mirex_key/audio/', filename);
  shiftFB = estimateTuning(f_audio);
  
  paramPitch.winLenSTMSP = 4410;
  paramPitch.shiftFB = shiftFB;
  paramPitch.visualize = 0;
  [f_pitch,sideinfo] = ...
    audio_to_pitch_via_FB(f_audio,paramPitch,sideinfo);

  paramCP.applyLogCompr = 0;
  paramCP.visualize = 0;
  paramCP.inputFeatureRate = sideinfo.pitch.featureRate;
  [f_CP,sideinfo] = pitch_to_chroma(f_pitch,paramCP,sideinfo);
  
  paramCLP.applyLogCompr = 1;
  paramCLP.factorLogCompr = 100;
  paramCLP.visualize = 0;
  paramCLP.inputFeatureRate = sideinfo.pitch.featureRate;
  [f_CLP,sideinfo] = pitch_to_chroma(f_pitch,paramCLP,sideinfo);
  
  paramCENS.winLenSmooth = 21;
  paramCENS.downsampSmooth = 5;
  paramCENS.visualize = 0;
  paramCENS.inputFeatureRate = sideinfo.pitch.featureRate;
  [f_CENS,sideinfo] = pitch_to_CENS(f_pitch,paramCENS,sideinfo);
  
  paramCRP.coeffsToKeep = [55:120];
  paramCRP.visualize = 0;
  paramCRP.inputFeatureRate = sideinfo.pitch.featureRate;
  [f_CRP,sideinfo] = pitch_to_CRP(f_pitch,paramCRP,sideinfo);    
  
  % Save chroma frame per frame
%   s = size(f_CP);
%   C = [zeros(1,s(2)); f_CP]; % Add time row (add zeros as we dont use it)
%   csvwrite(sprintf('toolbox_cp_csv/%02d.csv', i), C')
%   
%   s = size(f_CLP);
%   C = [zeros(1,s(2)); f_CLP]; % Add time row (add zeros as we dont use it)
%   csvwrite(sprintf('toolbox_clp_csv/%02d.csv', i), C')
%   
%   s = size(f_CENS);
%   C = [zeros(1,s(2)); f_CENS]; % Add time row (add zeros as we dont use it)
%   csvwrite(sprintf('toolbox_cens_csv/%02d.csv', i), C')
%   
%   s = size(f_CRP);
%   C = [zeros(1,s(2)); f_CRP]; % Add time row (add zeros as we dont use it)
%   csvwrite(sprintf('toolbox_crp_csv/%02d.csv', i), C')

  % Save key profile (chroma mean)
  csvwrite(sprintf('toolbox_cp_csv/%02d_avg.csv', i), mean(f_CP,2))
  csvwrite(sprintf('toolbox_clp_csv/%02d_avg.csv', i), mean(f_CLP,2))
  csvwrite(sprintf('toolbox_cens_csv/%02d_avg.csv', i), mean(f_CENS,2))
  csvwrite(sprintf('toolbox_crp_csv/%02d_avg.csv', i), mean(f_CRP,2))
    
  sprintf('%02d done!', i)
end

sprintf('Batch finished successfully!!!')

