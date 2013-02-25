clear
close all

filenames = {'melody4', 'ALoDown-mono', '07', 'extrabits'};
% filenames = {'melody4'};

%   [x, fs, nbits] = wavread(sprintf('../database/%s.wav', filename));
%   x = x(:,1); % take only 1 channel
%   soundsc(y, fs);

fig = 1;
for i=1:size(filenames,2)
  filename = sprintf('%s.wav', filenames{i});
  
  [f_audio,sideinfo] = wav_to_audio('', '../database/', filename);
  shiftFB = estimateTuning(f_audio);
  
  paramPitch.winLenSTMSP = 4410;
  paramPitch.shiftFB = shiftFB;
  paramPitch.visualize = 0;
  [f_pitch,sideinfo] = ...
    audio_to_pitch_via_FB(f_audio,paramPitch,sideinfo);
  
%   paramCP.applyLogCompr = 0;
%   paramCP.visualize = 1;
%   paramCP.inputFeatureRate = sideinfo.pitch.featureRate;
%   [f_CP,sideinfo] = pitch_to_chroma(f_pitch,paramCP,sideinfo);
%   
%   paramCLP.applyLogCompr = 1;
%   paramCLP.factorLogCompr = 100;
%   paramCLP.visualize = 1;
%   paramCLP.inputFeatureRate = sideinfo.pitch.featureRate;
%   [f_CLP,sideinfo] = pitch_to_chroma(f_pitch,paramCLP,sideinfo);
%   
%   paramCENS.winLenSmooth = 21;
%   paramCENS.downsampSmooth = 5;
%   paramCENS.visualize = 1;
%   paramCENS.inputFeatureRate = sideinfo.pitch.featureRate;
%   [f_CENS,sideinfo] = pitch_to_CENS(f_pitch,paramCENS,sideinfo);
  
  paramCRP.coeffsToKeep = [55:120];
  paramCRP.visualize = 1;
  paramCRP.inputFeatureRate = sideinfo.pitch.featureRate;
  [f_CRP,sideinfo] = pitch_to_CRP(f_pitch,paramCRP,sideinfo);
  
% Print and save figures
  title(sprintf('CRP chromagram | %s', filename)) % set title for already printed figure of CRP
  nameplot = sprintf('Chromagram_%s.jpg',filenames{i});
  saveas(figure(fig), nameplot)
  fig = fig + 1;
  
  figure
  bar(mean(f_CRP'));
  aux=(1:12);
  set(gca,'xtick',aux);
  set(gca,'XTickLabel',{'C';'C#';'D';'D#';'E';'F';'F#';'G';'G#';'A';'A#';'B';});
  grid
  title(sprintf('Average chroma features | %s',filenames{i}));
  
  nameplot = sprintf('InstantChroma_%s.jpg',filenames{i});
  saveas(figure(fig), nameplot)
  fig = fig + 1;
end