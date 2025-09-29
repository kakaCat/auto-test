// Monaco Editor Mock for Testing
export const editor = {
  create: vi.fn(() => ({
    getValue: vi.fn(() => ''),
    setValue: vi.fn(),
    onDidChangeModelContent: vi.fn((callback) => {
      // 返回一个 dispose 函数
      return { dispose: vi.fn() }
    }),
    onDidChangeCursorPosition: vi.fn((callback) => {
      // 返回一个 dispose 函数
      return { dispose: vi.fn() }
    }),
    dispose: vi.fn(),
    getModel: vi.fn(() => ({
      getLineCount: vi.fn(() => 1),
      getValue: vi.fn(() => ''),
      onDidChangeContent: vi.fn(() => ({ dispose: vi.fn() }))
    })),
    getPosition: vi.fn(() => ({ lineNumber: 1, column: 1 })),
    focus: vi.fn(),
    layout: vi.fn(),
    updateOptions: vi.fn(),
    deltaDecorations: vi.fn(() => []),
    getAction: vi.fn(() => ({
      run: vi.fn()
    })),
    trigger: vi.fn()
  })),
  setTheme: vi.fn(),
  defineTheme: vi.fn(),
  setModelLanguage: vi.fn(),
  setModelMarkers: vi.fn()
}

export const languages = {
  json: {
    jsonDefaults: {
      setDiagnosticsOptions: vi.fn()
    }
  },
  register: vi.fn(),
  setMonarchTokensProvider: vi.fn(),
  setLanguageConfiguration: vi.fn()
}

export const Range = class {
  constructor(startLineNumber, startColumn, endLineNumber, endColumn) {
    this.startLineNumber = startLineNumber
    this.startColumn = startColumn
    this.endLineNumber = endLineNumber
    this.endColumn = endColumn
  }
}

export const Selection = class extends Range {
  constructor(selectionStartLineNumber, selectionStartColumn, positionLineNumber, positionColumn) {
    super(selectionStartLineNumber, selectionStartColumn, positionLineNumber, positionColumn)
    this.selectionStartLineNumber = selectionStartLineNumber
    this.selectionStartColumn = selectionStartColumn
    this.positionLineNumber = positionLineNumber
    this.positionColumn = positionColumn
  }
}

export default {
  editor,
  languages,
  Range,
  Selection
}