%% preprocess the data
clc
clear
%% load data, as X
load dataLinear.mat
X = dataLinear;
[row col] = size(X);
Y = zeros(size(X));

%% interpolate the data, as Y
for ii = 1:row
    x = X(ii,:);
    dx = diff(x);
    index0 = find(dx ~= 0);
    value0 = [x(1) dx(index0)];
    value0 = cumsum(value0);
    index0 = [1 index0+1];
    if index0(end) ~= col
        index0 = [index0 col];
        value0 = [value0 X(ii,end)];
    end
    index1 = [1:col];
    value1 = interp1(index0,value0,index1,'cubic');
    Y(ii,:) = value1;
end
save Y Y
% load Y.mat

%% calculate the trends
P = 20;
trends = zeros(size(Y));
for ii = 1:row
    for jj = 1+P:col-P
        trends(ii,jj) = mean(X(ii,jj-P:jj+P));
    end
end

save trends trends

% load trends.mat

%% calculate the residual, as Z
Z = Y-trends;
% remove bad parts
Z = Z(:,1+P:end-P);

%% load motionCode, as motion
load motionCode.mat
motion = motionCode(1+P:end-P);

%% trim Y, Z and motion
Y = Y(:,1+P:end-P);
Y = Y(:,25:end);
Z = Z(:,25:end);
motion = motion(:,25:end);

%% finally we obtain Y, Z and motion
% where Y is the original data (interpolated), Z is the detrended data

save Y Y
save Z Z
save motion motion

