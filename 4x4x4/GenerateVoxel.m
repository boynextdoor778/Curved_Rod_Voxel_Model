function [voxel,Density] = GenerateVoxel(n,address,radius)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% n is the number of voxel along each axis
% address is the file location of wireframe
% density is the relative density
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
size = 1/n;               % initial size of voxels
voxel = zeros(n,n,n);      % initial grid with zeros
%% generate a list of centers of voxel
voxel_c = zeros(n^3,6);   
p = 0;                    % p count the number of all voxels
for i = 1:n               % i for z axis
    for j = 1:n           % j for y axis
        for k = 1:n       % k for x axis
            p = p + 1;
            voxel_c(p,1:3) = [k,j,i];  % save index along x,y,z axis
            % save coordinate along x,y,z axis
            voxel_c(p,4:6) = [(k-0.5)*size,(j-0.5)*size,(i-0.5)*size];         
        end
    end
end
%% Get the voxel close the the strut witnin a certain distance
[node,strut] = ReadStrut(address); % get the information of strut
for i = 1:length(voxel_c)          % for each voxel, deside if it is active
    % for each strut, get the distance to the voxel
    for j = 1:length(strut)        
        start_n = node(strut(j,1),:);  % start node coordinate
        end_n = node(strut(j,2),:);    % end node coordinate
        center = voxel_c(i,4:6);        % voxel center position
        % determine alpha and beta are acute angle
        alpha = acosd(((center - start_n)*(end_n - start_n)')...
            /(norm(center - start_n)*norm(end_n - start_n)));
        beta = acosd(((center - end_n)*(start_n - end_n)')...
            /(norm(center - end_n)*norm(start_n - end_n)));
        if(alpha<90 && beta<90)% if not acute angle, distance to line
            distance = norm(cross(end_n - start_n,center - start_n))...
                /norm(end_n - start_n);
        else                      % if it is acute angle, distance to node
            distance = min(norm(center - start_n),norm(center - end_n));
        end
        if (distance<=radius)     % if distance less than radius, active it
            voxel(voxel_c(i,1),voxel_c(i,2),voxel_c(i,3)) = 1;
            continue;             % run for the next voxel
        end
    end
end
Density = sum(sum(sum(voxel)))/n^3 % calculate the relative density
end
%%Import information of strut
function [nodelist,strutlist] = ReadStrut(address)
fid = fopen(address,'r');
if fid == -1
    error('Cannot open topology file: %s', address);
end

nodelist = [];
strutlist = [];

tline = fgetl(fid);
while ischar(tline)
    tline = strtrim(tline);

    % skip empty lines and comments
    if isempty(tline) || startsWith(tline, '//')
        tline = fgetl(fid);
        continue;
    end

    if startsWith(tline, 'GRID')
        vals = sscanf(tline, 'GRID %d %f %f %f');
        if numel(vals) == 4
            idx = vals(1);
            nodelist(idx,1:3) = vals(2:4).';
        end
    elseif startsWith(tline, 'STRUT')
        vals = sscanf(tline, 'STRUT %d %d %d');
        if numel(vals) == 3
            idx = vals(1);
            strutlist(idx,1:2) = vals(2:3).';
        end
    end

    tline = fgetl(fid);
end

fclose(fid);
end

