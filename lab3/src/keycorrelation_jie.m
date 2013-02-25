function [note, mode] = keycorrelation(chroma)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here
M = [6.35 2.23 3.48 2.33 4.38 4.09 2.52 5.19 2.39 3.66 2.29 2.88];
m = [6.33 2.68 3.52 5.38 2.6 3.53 2.54 4.75 3.98 2.69 3.34 3.17];
chroma=mean(chroma');
mean_chroma=mean(chroma);
var_chroma=std(chroma);
mean_M=mean(M);
var_M=std(M);
mean_m=mean(m);
var_m=std(m);
R=zeros(2,12);
for i=1:12
    temp_M=M(mod([1:12]-i+12, 12)+1);
    temp_m=m(mod([1:12]-i+12, 12)+1);
    R(1,i)=sum((chroma-mean_chroma).*(temp_M-mean_M))/(var_chroma*var_M);
    R(2,i)=sum((chroma-mean_chroma).*(temp_m-mean_m))/(var_chroma*var_m);
end
R=R';
[~,index]=max(R(:));
mode=floor((index-1)/12);
note=index-mode*12-1;
newnote=mod(note+5,12);

%optimization
if R(newnote+1,mode+1) / R(note+1, mode+1) > 0.5
    note=newnote;
end
if mode == 1
    newnote=mod(note+3,12);
    if R(newnote+1, 1) / R(note+1, 2) > 0.85
        note=newnote;
        mode=0;
    end
end

if mode == 0 && R(note+1, 2) / R(note+1,1) > 0.65
    mode = 1;
end
end

