import '@testing-library/jest-dom/vitest';
import { vi } from 'vitest';
import React from 'react';

vi.mock('echarts-for-react', () => ({
  default: () => React.createElement('div', { 'data-testid': 'mock-echarts' }),
}));
