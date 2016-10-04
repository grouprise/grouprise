function inequality(v1, v2) {
    return v1 !== v2;
}

function equality(v1, v2) {
    return v1 === v2;
}

function all(values, expect, cmp = equality) {
    return values.reduce((result, value) => result && cmp(value, expect));
}

function list(v1, v2, cmp = equality) {
    if(v1.length !== v2.length) {
        throw new Error("invalid list comparison with differing lengths");
    }

    const results = [];

    for(let i = 0, length = v1.length; i < length; i++) {
        results.push(cmp(v1[i], v2[i]));
    }

    return all(results, true);
}

export default { inequality, equality, all, list };
