var getAreaInSquareMillimiters = function(areaInMicrons, decimalDigits) {
    return Number((areaInMicrons / Math.pow(10, 6)).toFixed(decimalDigits));
};

var getLengthInMillimiters = function(lengthInMicrons, decimalDigits) {
    return Number((lengthInMicrons / Math.pow(10, 3)).toFixed(decimalDigits));
};