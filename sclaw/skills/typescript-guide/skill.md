---
name: typescript-guide
description: TypeScript 开发最佳实践和编码规范，包括类型定义、接口使用、泛型等
triggers:
  - typescript
  - ts
  - 类型定义
  - interface
  - 泛型
---

# TypeScript 开发指南

## 类型定义原则

### 1. 优先使用 interface 而非 type
```typescript
// ✅ 推荐
interface User {
  id: string;
  name: string;
}

// ❌ 避免
type User = {
  id: string;
  name: string;
}
```

### 2. 使用联合类型和交叉类型
```typescript
// 联合类型
type Status = 'pending' | 'active' | 'completed';

// 交叉类型
type AdminUser = User & {
  permissions: string[];
};
```

### 3. 避免使用 any
```typescript
// ✅ 推荐
function processData(data: unknown) {
  if (typeof data === 'string') {
    return data.toUpperCase();
  }
}

// ❌ 避免
function processData(data: any) {
  return data.toUpperCase();
}
```

## 接口使用

### 1. 可选属性
```typescript
interface Config {
  required: string;
  optional?: string;
}
```

### 2. 只读属性
```typescript
interface User {
  readonly id: string;
  name: string;
}
```

### 3. 函数类型
```typescript
interface SearchFunc {
  (source: string, subString: string): boolean;
}
```

## 泛型使用

### 1. 基本泛型
```typescript
function identity<T>(arg: T): T {
  return arg;
}
```

### 2. 泛型约束
```typescript
interface Lengthwise {
  length: number;
}

function loggingIdentity<T extends Lengthwise>(arg: T): T {
  console.log(arg.length);
  return arg;
}
```

### 3. 泛型接口
```typescript
interface Box<T> {
  value: T;
}
```

## 类型推断

### 1. 自动推断
```typescript
// TypeScript 会自动推断 x 的类型为 number
let x = 3;
```

### 2. 最佳通用类型
```typescript
// 推断为 number[]
let x = [0, 1, null];

// 推断为 (number | null)[]
let y = [0, 1, null] as const;
```

## 类型守卫

### 1. typeof
```typescript
function padLeft(value: string, padding: string | number) {
  if (typeof padding === 'number') {
    return Array(padding + 1).join(' ') + value;
  }
  return padding + value;
}
```

### 2. instanceof
```typescript
function logValue(x: Date | string) {
  if (x instanceof Date) {
    console.log(x.toUTCString());
  } else {
    console.log(x.toUpperCase());
  }
}
```

## 最佳实践

1. **严格模式**：始终启用 `strict: true`
2. **类型导出**：导出类型供其他模块使用
3. **避免类型断言**：除非必要，不要使用 `as`
4. **使用工具类型**：`Partial<T>`, `Required<T>`, `Readonly<T>`
5. **命名约定**：接口使用 PascalCase，类型使用 PascalCase
