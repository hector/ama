clear all
close all

filenames = {'melody4', 'ALoDown-mono', '07', 'extrabits'};
%filenames = {'melody4'};
for i=1:size(filenames,2)
    % Read from CSV
    C = csvread(sprintf('hpcp_csv/%s_vamp_vamp-hpcp-mtg_MTG-HPCP_HPCP.csv',filenames{i}))';
    tt = C(1,:);
    clear C2
    C2(1:9,:) = C(5:13,:);
    C2(10:12,:) = C(2:4,:);
    clear C
    C = C2;
    
    % Plot Chromagram
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
    saveas(figure(fig), nameplot);

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
    saveas(figure(fig), nameplot);
end