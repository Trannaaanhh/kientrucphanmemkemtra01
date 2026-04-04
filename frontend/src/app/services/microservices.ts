import { apiRequest } from "./api";

// 1. Tích hợp API: Gọi API Gateway cho 3 service

export const checkInventoryAPI = async (items: { product_id: string; quantity: number }[], token: string) => {
  return await apiRequest<{ error?: string; status?: string }>("/inventory/check", {
    method: "POST",
    token,
    body: { items },
  });
};

// Response của order-service có thể trả về thông tin order, bao gồm id và transaction_id
export const createOrderAPI = async (items: { product_id: string; quantity: number }[], totalAmount: number, token: string) => {
  return await apiRequest<{ id: string; transaction_id: string }>("/orders/", {
    method: "POST",
    token,
    body: { items, total_amount: totalAmount },
  });
};

export const processPaymentAPI = async (orderId: string, transactionId: string, amount: number, token: string) => {
  return await apiRequest("/payment/create", {
    method: "POST",
    token,
    body: { order_id: orderId, transaction_id: transactionId, amount },
  });
};

// --- Staff Management APIs ---

export const getInventoryAPI = async (token: string) => {
  return await apiRequest<Array<{ product_id: string; quantity: number }>>("/inventory/", { token });
};

export const updateInventoryAPI = async (items: { product_id: string; quantity: number }[], token: string) => {
  return await apiRequest("/inventory/", {
    method: "POST",
    token,
    body: { items },
  });
};

export const getOrdersAPI = async (token: string) => {
  return await apiRequest<Array<any>>("/orders/", { token });
};

export const getPaymentsAPI = async (token: string) => {
  return await apiRequest<Array<any>>("/payment/", { token });
};
