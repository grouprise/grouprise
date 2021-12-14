module.exports = {
  root: true,
  env: {
    node: true
  },
  'extends': [
    'plugin:vue/recommended'
  ],
  rules: {
    'no-console': 'off',
    'no-debugger': 'off',
    'indent': 'off',
    'vue/script-indent': [
      'warn',
      2,
      {
        'baseIndent': 1,
        'switchCase': 1
      }
    ]
  },
  parserOptions: {
    parser: '@babel/eslint-parser'
  }
}
