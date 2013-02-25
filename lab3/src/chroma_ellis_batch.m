clear all
close all

% filenames = {'melody4', 'ALoDown-mono', '07', 'extrabits'};
%filenames = {'melody4'};

for i=1:96
%     filename = filenames{i};
    [d, sr, nbits] = wavread(sprintf('../mirex_key/audio/%02d.wav', i));
    d = d(:,1); % take only 1 channel
    %soundsc(y, fs);

    % Calculate the chroma matrix.  Use a long FFT to discriminate
    % spectral lines as well as possible (2048 is the default value)
    cfftlen=2048;
    C = chromagram_IF(d,sr,cfftlen);
    
    clear C2
    C2(1:9,:) = C(4:12,:);
    C2(10:12,:) = C(1:3,:);
    
%     s = size(C2);
%     chroma = [linspace(0, length(d)/sr, s(2)); C2]'; % Add time row
    
%     csvwrite(sprintf('ellis_csv/%02d.csv', i), chroma);
%     dlmwrite(sprintf('ellis_csv/%02d.csv', i), chroma, 'precision',
%     '%10.10f'); % specify format

    csvwrite(sprintf('ellis_csv/%02d_avg.csv', i), mean(C2,2)); % save key profile
    
    sprintf('%02d done!', i)
    
    % The frame advance is always one quarter of the FFT length.  Thus,
    % the columns  of C are at timebase of fftlen/4/sr
%     tt = [1:size(C,2)]*cfftlen/4/sr;

    % Plot chromagram using a shorter window, also on a dB magnitude scale
%     fig = 1;
%     figure(fig)
%     imagesc(tt,[1:12],20*log10(C+eps));
%     axis xy
%     caxis(max(caxis)+[-60 0])
%     aux=(1:12); 
%     set(gca,'ytick',aux); 
%     set(gca,'YTickLabel',{'C';'C#';'D';'D#';'E';'F';'F#';'G';'G#';'A';'A#';'B'});
%     title(sprintf('Chromagram | %s.wav',filenames{i}))
%     
%     nameplot = sprintf('Chromagram_%s.jpg',filenames{i});
%     saveas(figure(fig), nameplot);
    
%     % Plot average chroma features
%     fig = fig+1;
%     figure(fig) 
%     bar(mean(C')); 
%     set(gca,'xtick',aux); 
% %    set(gca,'XTickLabel',{'A';'A#';'B';'C';'C#';'D';'D#';'E';'F';'F#';'G';'G#'; });
%     set(gca,'XTickLabel',{'C';'C#';'D';'D#';'E';'F';'F#';'G';'G#';'A';'A#';'B'});
%     grid
%     title(sprintf('Average chroma features | %s.wav',filenames{i}));
% % 
%     nameplot = sprintf('InstantChroma_%s.jpg',filenames{i});
%     saveas(figure(fig), nameplot);
end

sprintf('Batch finished successfully!!!')