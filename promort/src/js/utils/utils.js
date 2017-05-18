var formatDecimalNumber = function(number, decimal_digits) {
    return Number(number.toFixed(decimal_digits));
};

var removeItemFromArray = function(item_value, array) {
    var item_index = array.indexOf(item_value);
    if (item_index !== -1) {
        return array.splice(item_index, 1);
    }
    return false;
};
