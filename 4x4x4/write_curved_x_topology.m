function write_curved_x_topology(outFile, nPtsPerArm, bendAmp, refAxis)
% Curved-X topology with FIXED GLOBAL bend direction.
%
% refAxis = global bend direction
%   XY正视图保持标准X  -> refAxis = [0 0 1]
%   XZ正视图保持标准X  -> refAxis = [0 1 0]
%   YZ正视图保持标准X  -> refAxis = [1 0 0]

    if nargin < 4 || isempty(refAxis)
        refAxis = [0 0 1];
    end

    validateattributes(nPtsPerArm, {'numeric'}, {'scalar','integer','>=',3});
    validateattributes(bendAmp, {'numeric'}, {'scalar','>=',0});
    validateattributes(refAxis, {'numeric'}, {'vector','numel',3});

    bendDir = refAxis(:).';
    if norm(bendDir) < 1e-12
        error('refAxis cannot be zero.');
    end
    bendDir = bendDir / norm(bendDir);

    corners = [ ...
        0 0 0;
        1 1 1;
        1 0 0;
        0 1 1;
        0 1 0;
        1 0 1;
        1 1 0;
        0 0 1];

    center = [0.5 0.5 0.5];

    nodeList = [];
    strutList = [];

    % shared center node
    nodeList(end+1, :) = center;
    centerID = 1;

    for k = 1:size(corners,1)
        p0 = corners(k, :);
        p1 = center;
        pairSign = sign(dot(p0 - center, bendDir));
        if pairSign == 0
            pairSign = 1;
        end

        % sampled points along the body diagonal
        t = linspace(0, 1, nPtsPerArm).';

        % straight mother line
        P = p0 + t .* (p1 - p0);

        % multi-bend waveform, keep your previous style
        nWave = 2.0;
        env   = (sin(pi*t)).^2;
        wave  = sin(2*pi*nWave*t) .* env;

        % apply FIXED GLOBAL bend direction
        P = P + pairSign * bendAmp * wave .* bendDir;

        armIDs = zeros(nPtsPerArm, 1);

        % keep all points except the final center point, which is shared
        for i = 1:nPtsPerArm-1
            nodeList(end+1, :) = P(i, :);
            armIDs(i) = size(nodeList, 1);
        end
        armIDs(end) = centerID;

        % connect adjacent sampled points
        for i = 1:nPtsPerArm-1
            strutList(end+1, :) = [armIDs(i), armIDs(i+1)];
        end
    end

    fid = fopen(outFile, 'w');
    if fid == -1
        error('Cannot open file for writing: %s', outFile);
    end
    cleanupObj = onCleanup(@() fclose(fid)); %#ok<NASGU>

    fprintf(fid, '//Grid  ID      x       y       z\n');
    for i = 1:size(nodeList,1)
        fprintf(fid, 'GRID    %d %.6f %.6f %.6f\n', ...
            i, nodeList(i,1), nodeList(i,2), nodeList(i,3));
    end

    fprintf(fid, '//Strut ID      Start   End\n');
    for i = 1:size(strutList,1)
        fprintf(fid, 'STRUT   %d %d %d\n', ...
            i, strutList(i,1), strutList(i,2));
    end
end