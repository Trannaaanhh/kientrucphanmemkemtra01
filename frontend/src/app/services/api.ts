const API_BASE_URL = "/api";

type ApiOptions = {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: unknown;
  token?: string;
};

export async function apiRequest<T>(path: string, options: ApiOptions = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: options.method ?? "GET",
      headers: {
        "Content-Type": "application/json",
        ...(options.token ? { Authorization: `Bearer ${options.token}` } : {}),
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new Error("Khong the ket noi API Gateway (localhost:8080)");
  }

  const rawText = await response.text();
  const contentType = response.headers.get("content-type") || "";
  const isJson = contentType.includes("application/json");

  let data: any = {};
  if (rawText && isJson) {
    try {
      data = JSON.parse(rawText);
    } catch {
      data = {};
    }
  }

  if (!response.ok) {
    // Handle token expiration errors
    if (response.status === 401 && (data.error?.includes("Token expired") || data.error?.includes("Invalid") || data.error?.includes("Missing"))) {
      clearAuth();
      const isStaff = window.location.pathname.startsWith("/staff");
      window.location.href = isStaff ? "/staff/login" : "/customer/login";
      throw new Error("Session expired. Redirecting to login...");
    }

    const serverMessage = typeof data?.error === "string" ? data.error : rawText.trim();
    throw new Error(serverMessage || "Request failed");
  }
  return data as T;
}

export function saveAuthToken(token: string, role: "customer" | "staff") {
  localStorage.setItem(`kt01_${role}_token`, token);
  localStorage.setItem(`kt01_${role}_role`, role);
}

export function saveUserInfo(role: "customer" | "staff", name: string, email: string) {
  localStorage.setItem(`kt01_${role}_name`, name);
  localStorage.setItem(`kt01_${role}_email`, email);
}

export function getUserName(): string {
  const isStaff = window.location.pathname.startsWith("/staff");
  return localStorage.getItem(`kt01_${isStaff ? "staff" : "customer"}_name`) || "";
}

export function getUserEmail(): string {
  const isStaff = window.location.pathname.startsWith("/staff");
  return localStorage.getItem(`kt01_${isStaff ? "staff" : "customer"}_email`) || "";
}

export function getAuthToken() {
  const isStaff = window.location.pathname.startsWith("/staff");
  return localStorage.getItem(`kt01_${isStaff ? "staff" : "customer"}_token`) || "";
}

export function getAuthRole() {
  const isStaff = window.location.pathname.startsWith("/staff");
  return localStorage.getItem(`kt01_${isStaff ? "staff" : "customer"}_role`) || "";
}

export function clearAuth() {
  const isStaff = window.location.pathname.startsWith("/staff");
  const prefix = `kt01_${isStaff ? "staff" : "customer"}`;
  localStorage.removeItem(`${prefix}_token`);
  localStorage.removeItem(`${prefix}_role`);
  localStorage.removeItem(`${prefix}_name`);
  localStorage.removeItem(`${prefix}_email`);
}
