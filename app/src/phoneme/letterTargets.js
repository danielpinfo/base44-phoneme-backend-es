// app/src/phoneme/letterTargets.js

export const LETTER_TARGETS = {
  en: {
    A: { ipa: ['æ', 'eɪ', 'ɑː'], base44: [] },
    B: { ipa: ['b'], base44: [] },
    C: { ipa: ['k', 's'], base44: [] },
    D: { ipa: ['d'], base44: [] },
    E: { ipa: ['iː', 'ɛ'], base44: [] },
    F: { ipa: ['f'], base44: [] },
    G: { ipa: ['ɡ', 'dʒ'], base44: [] },
    H: { ipa: ['h'], base44: [] },
    I: { ipa: ['aɪ', 'ɪ'], base44: [] },
    J: { ipa: ['dʒ'], base44: [] },
    K: { ipa: ['k'], base44: [] },
    L: { ipa: ['l'], base44: [] },
    M: { ipa: ['m'], base44: [] },
    N: { ipa: ['n'], base44: [] },
    O: { ipa: ['oʊ', 'ɒ', 'ɑː'], base44: [] },
    P: { ipa: ['p'], base44: [] },
    Q: { ipa: ['k'], base44: [] },
    R: { ipa: ['ɹ', 'r'], base44: [] },
    S: { ipa: ['s', 'z'], base44: [] },
    T: { ipa: ['t'], base44: [] },
    U: { ipa: ['uː', 'ʌ', 'juː'], base44: [] },
    V: { ipa: ['v'], base44: [] },
    W: { ipa: ['w'], base44: [] },
    X: { ipa: ['ks', 'gz'], base44: [] },
    Y: { ipa: ['j', 'aɪ', 'ɪ'], base44: [] },
    Z: { ipa: ['z', 's'], base44: [] },
  },

  es: {
    A: { ipa: ['a'], base44: [] },
    B: { ipa: ['b', 'β'], base44: [] },
    C: { ipa: ['k', 'θ', 's'], base44: [] },
    D: { ipa: ['d', 'ð'], base44: [] },
    E: { ipa: ['e'], base44: [] },
    F: { ipa: ['f'], base44: [] },
    G: { ipa: ['g', 'ɣ', 'x'], base44: [] },

    H: { ipa: [], base44: [], behavior: 'silent' },

    I: { ipa: ['i'], base44: [] },
    J: { ipa: ['x'], base44: [] },
    K: { ipa: ['k'], base44: [] },
    L: { ipa: ['l'], base44: [] },

    LL: { ipa: ['ʎ', 'ʝ', 'j'], base44: [] },

    M: { ipa: ['m'], base44: [] },
    N: { ipa: ['n'], base44: [] },
    Ñ: { ipa: ['ɲ'], base44: [] },

    O: { ipa: ['o'], base44: [] },
    P: { ipa: ['p'], base44: [] },
    Q: { ipa: ['k'], base44: [] },
    R: { ipa: ['ɾ', 'r'], base44: [] },
    S: { ipa: ['s'], base44: [] },
    T: { ipa: ['t'], base44: [] },
    U: { ipa: ['u'], base44: [] },
    V: { ipa: ['b', 'β'], base44: [] },
    W: { ipa: ['w'], base44: [] },
    X: { ipa: ['ks', 's', 'x'], base44: [] },
    Y: { ipa: ['ʝ', 'j', 'i'], base44: [] },
    Z: { ipa: ['θ', 's'], base44: [] },
  },
};

