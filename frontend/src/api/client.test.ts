import { describe, it, expect, vi, beforeEach } from 'vitest';
import { apiClient, ApiError } from './client';

describe('apiClient', () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it('fetches metadata successfully', async () => {
    const mockMeta = {
      decision_date_from: '2026-01-01',
      decision_date_to: '2026-01-31',
      delivery_date_from: '2026-01-02',
      delivery_date_to: '2026-02-01',
      default_cutoff_time: '09:00',
      timezone: 'Europe/London',
      error_convention: 'error = forecast - actual',
      actuals_row_count: 1488,
      forecasts_row_count: 15775,
    };

    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockMeta,
    } as Response);

    const result = await apiClient.getMeta();
    expect(result.delivery_date_from).toBe('2026-01-02');
    expect(result.actuals_row_count).toBe(1488);
  });

  it('throws ApiError on non-ok responses', async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      text: async () => 'Not Found',
    } as Response);

    await expect(apiClient.getDecisionForecast('2026-01-02', '09:00')).rejects.toThrow(ApiError);
  });
});
