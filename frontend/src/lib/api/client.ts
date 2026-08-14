const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api/v1";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly code = "API_ERROR",
    public readonly requestId?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type ApiErrorBody = {
  error?: { code?: string; message?: string; request_id?: string };
};

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const isFormData = init?.body instanceof FormData;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { ...(isFormData ? {} : { "Content-Type": "application/json" }), ...init?.headers },
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as ApiErrorBody;
    throw new ApiError(
      body.error?.message ?? "请求失败",
      response.status,
      body.error?.code,
      body.error?.request_id ?? response.headers.get("X-Request-ID") ?? undefined,
    );
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function apiDownload(path: string): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  if (!response.ok) throw new ApiError("导出失败", response.status);
  return response.blob();
}

export const apiClient = {
  get: <T>(path: string) => apiRequest<T>(path),
  post: <T>(path: string, body: unknown) =>
    apiRequest<T>(path, { method: "POST", body: JSON.stringify(body) }),
  put: <T>(path: string, body: unknown) =>
    apiRequest<T>(path, { method: "PUT", body: JSON.stringify(body) }),
  delete: <T>(path: string) => apiRequest<T>(path, { method: "DELETE" }),
};
