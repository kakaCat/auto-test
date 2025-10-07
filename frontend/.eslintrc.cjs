/* eslint-env node */
module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true
  },
  extends: [
    'eslint:recommended',
    'plugin:vue/vue3-recommended',
    'plugin:@typescript-eslint/recommended'
  ],
  parser: 'vue-eslint-parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    extraFileExtensions: ['.vue'],
    parser: '@typescript-eslint/parser',
    warnOnUnsupportedTypeScriptVersion: false
  },
  plugins: [
    'vue',
    '@typescript-eslint'
  ],
  overrides: [
    {
      files: ['*.vue'],
      parser: 'vue-eslint-parser',
      parserOptions: {
        parser: '@typescript-eslint/parser'
      }
    },
    {
      files: ['**/*.cjs', '**/*.config.js', '**/*.config.cjs'],
      rules: {
        '@typescript-eslint/no-var-requires': 'off',
        'no-var': 'off'
      }
    },
    {
      files: ['src/test/**/*.js', '**/*.spec.{js,ts,vue}', '**/*.test.{js,ts,vue}'],
      globals: {
        vi: 'readonly',
        afterEach: 'readonly',
        beforeEach: 'readonly',
        describe: 'readonly',
        it: 'readonly',
        expect: 'readonly'
      }
    },
    {
      files: ['src/views/api-management/**/*.{ts,vue}'],
      rules: {
        '@typescript-eslint/no-explicit-any': 'off'
      }
    }
  ],
  rules: {
    // Vue 相关规则
    'vue/multi-word-component-names': 'off',
    'vue/no-mutating-props': 'off',

    // 通用规则
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-useless-escape': 'off',
    'no-prototype-builtins': 'off',

    // TypeScript 规则调整：减少改造期的噪音
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/no-unused-vars': 'off',
    '@typescript-eslint/no-var-requires': 'off',
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/ban-types': 'off',
    '@typescript-eslint/ban-ts-comment': 'off',

    // JS 规则：在 switch/case 中允许声明
    'no-case-declarations': 'off',

    // 降低易误报/影响开发的规则
    'no-empty': 'off',
    'no-unexpected-multiline': 'off',
    'no-undef': 'off',
    'no-unused-vars': 'off',

    // Vue 模板样式规则：减少提示噪音
    'vue/html-indent': 'off',
    'vue/max-attributes-per-line': 'off',
    'vue/attributes-order': 'off',
    'vue/first-attribute-linebreak': 'off',
    'vue/singleline-html-element-content-newline': 'off',
    'vue/multiline-html-element-content-newline': 'off',
    'vue/no-self-closing': 'off',
    'vue/no-v-text': 'off',
    'vue/no-useless-template-attributes': 'off',
    'vue/require-default-prop': 'off',
    'vue/no-template-shadow': 'off',
    'vue/require-prop-types': 'off'
  },
  globals: {
    ElMessage: 'readonly',
    ElMessageBox: 'readonly',
    ElLoading: 'readonly',
    ElNotification: 'readonly'
  },
  ignorePatterns: [
    '*.d.ts'
  ]
}