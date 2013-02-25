clear all
close all

filenames = {'melody4', 'ALoDown-mono', '07', 'extrabits'};
%filenames = {'melody4'};

for i=1:size(filenames,2)
    filename = filenames{i};
    [d, sr, nbits] = wavread(sprintf('../database/%s.wav', filename));
    d = d(:,1); % take only 1 channel
    %soundsc(y, fs);

    % Calculate the chroma matrix.  Use a long FFT to discriminate
    % spectral lines as well as possible (2048 is the default value)
    cfftlen=2048;
    C = chromagram_IF(d,sr,cfftlen);
    clear C2
    C2(1:9,:) = C(4:12,:);
    C2(10:12,:) = C(1:3,:);
    clear C
    C = C2;
    % The frame advance is always one quarter of the FFT length.  Thus,
    % the columns  of C are at timebase of fftlen/4/sr
    tt = [1:size(C,2)]*cfftlen/4/sr;

    % Plot chromagram using a shorter window, also on a dB magnitude scale
    fig = 1;
    figure(fig)
    imagesc(tt,[1:12],20*log10(C+eps));
    axis xy
    caxis(max(caxis)+[-60 0])
    aux=(1:12); 
    set(gca,'ytick',aux); 
    set(gca,'YTickLabel',{'C';'C#';'D';'D#';'E';'F';'F#';'G';'G#';'A';'A#';'B'});
    title(sprintf('Chromagram | %s.wav',filenames{i}))
    
    nameplot = sprintf('Chromagram_%s.jpg',filenames{i});
%     saveas(figure(fig), nameplot);
    
    % Plot average chroma features
    fig = fig+1;
    figure(fig) 
    bar(mean(C')); 
    set(gca,'xtick',aux); 
%    set(gca,'XTickLabel',{'A';'A#';'B';'C';'C#';'D';'D#';'E';'F';'F#';'G';'G#'; });
    set(gca,'XTickLabel',{'C';'C#';'D';'D#';'E';'F';'F#';'G';'G#';'A';'A#';'B'});
    grid
    title(sprintf('Average chroma features | %s.wav',filenames{i}));

    nameplot = sprintf('InstantChroma_%s.jpg',filenames{i});
%     saveas(figure(fig), nameplot);
    
        %% Chroma Synthesis
    % The chroma representation tells us the intensity of each of the 
    % 12 distinct musical chroma of the octave at each time frame.  We
    % can turn this back into an audio signal simply by using the 12
    % chroma values to modulate 12 sinusoids, tuned to cover one
    % octave.  However, that octave would be arbitrary, so instead, 
    % in <chromasynth.m chromasynth>, 
    % we use each chroma value to modulate an
    % ensemble of sinusoids, with frequencies that are related by
    % powers of two, all of which share the same chroma.  By applying a
    % smooth rolloff to these sinusoids at high and low extremes of the
    % spectrum, these tones carry chroma without a clear sense of
    % octave.  They are known as "Shepard Tones" for Roger Shepard, the
    % Stanford psychologist who first investigated their perceptual
    % properties.  chromasynth.m relies on  
    % <synthtrax.m synthtrax> to convert
    % frequency/magnitude vector pairs into waveform. 

    % chromsynth takes a chroma matrix as the first argument, the
    % *period* (in seconds) corresponding to each time frame, and 
    % the sampling rate for the waveform to be generated.
    x = chromsynth(C,cfftlen/4/sr,sr);
    % Plot this alongside the others to see how it differs
    sfftlen = 512;
    fig = fig+1;
    figure(fig)
    specgram(x,sfftlen,sr);
    caxis(max(caxis)+[-60 0])
    axis([0 length(d)/sr 0 4000])
    title(sprintf('Shepard tone resynthesis | %s.wav',filenames{i}));
    
    nameplot = sprintf('resynth_%s.jpg',filenames{i});
    saveas(figure(fig), nameplot);
    
    % Of course, the main point is to listen to the resynthesis:
%     soundsc(x,sr);
%     wavwrite(x,sr,'piano-shepard.wav');
    wavwrite(x,sr,sprintf('ellis_synth/synth_shepard_%s.wav',filenames{i}));
end