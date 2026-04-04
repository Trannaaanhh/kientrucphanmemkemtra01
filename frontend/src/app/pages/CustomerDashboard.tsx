import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import {
  Search, ShoppingCart, LogOut, Laptop, Smartphone, Monitor,
  Plus, Minus, Trash2, CheckCircle2, MapPin, Truck, Package, MessageCircle, Send, Sparkles,
} from "lucide-react";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "../components/ui/sheet";
import { Label } from "../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { type Product, type CartItem } from "../data/mockData";
import { apiRequest, clearAuth, getAuthRole, getAuthToken, getUserEmail, getUserName } from "../services/api";
import { checkInventoryAPI, createOrderAPI, processPaymentAPI } from "../services/microservices";

type ShippingMethod = "standard" | "express" | "same_day";

interface ShippingInfo {
  fullName: string;
  email: string;
  phone: string;
  address: string;
  district: string;
  city: string;
  note: string;
  shippingMethod: ShippingMethod;
}

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface ChatApiResponse {
  action?: string;
  response?: string;
  message?: string;
  products?: Array<Partial<Product>>;
}

const SHIPPING_OPTIONS: { value: ShippingMethod; label: string; desc: string; price: number; icon: string }[] = [
  { value: "standard", label: "Giao tiêu chuẩn", desc: "3–5 ngày làm việc", price: 30000, icon: "📦" },
  { value: "express",  label: "Giao nhanh",      desc: "1–2 ngày làm việc", price: 60000, icon: "🚀" },
  { value: "same_day", label: "Giao trong ngày",  desc: "Trong 4–6 giờ",     price: 100000, icon: "⚡" },
];

export function CustomerDashboard() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [cart, setCart] = useState<CartItem[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'laptop' | 'mobile' | 'pc'>('all');
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatSuggestions, setChatSuggestions] = useState<Product[]>([]);
  const [isSendingChat, setIsSendingChat] = useState(false);

  // Flow: 'shop' → 'shipping' → 'done'
  const [flowStep, setFlowStep] = useState<'shop' | 'shipping' | 'done'>('shop');
  const [orderSummary, setOrderSummary] = useState({ totalAmount: 0, itemCount: 0, items: [] as CartItem[] });

  const [shipping, setShipping] = useState<ShippingInfo>({
    fullName: "",
    email: "",
    phone: "",
    address: "",
    district: "",
    city: "TP. Hồ Chí Minh",
    note: "",
    shippingMethod: "standard",
  });
  const [shippingErrors, setShippingErrors] = useState<Partial<Record<keyof ShippingInfo, string>>>({});

  const token = getAuthToken();

  // Pre-fill name/email from login
  useEffect(() => {
    const savedName = getUserName();
    const savedEmail = getUserEmail();
    setShipping(prev => ({
      ...prev,
      fullName: savedName || prev.fullName,
      email: savedEmail || prev.email,
    }));
  }, []);

  useEffect(() => {
    const role = getAuthRole();
    if (role !== "customer" || !token) {
      clearAuth();
      navigate("/customer/login");
      return;
    }

    apiRequest<{ items: Array<{ product_id?: string; id?: string; name: string; category: "laptop" | "mobile" | "pc"; price: number; quantity: number; image: string; brand: string; specs: string }> }>("/customer/cart", { token })
      .then((data) => {
        const items: CartItem[] = data.items.map((item) => ({
          id: item.id ?? item.product_id ?? "",
          name: item.name,
          category: item.category,
          price: Number(item.price),
          quantity: Number(item.quantity),
          image: item.image,
          brand: item.brand,
          specs: item.specs,
          stock: 0,
        }));
        setCart(items);
      })
      .catch(() => {});
  }, [navigate, token]);

  useEffect(() => {
    const role = getAuthRole();
    if (role !== "customer" || !token) return;

    const categoryParam = selectedCategory === "all" ? "all" : selectedCategory;
    apiRequest<{ items: Product[] }>(`/catalog/search?q=${encodeURIComponent(searchQuery)}&category=${categoryParam}`, { token })
      .then((data) => setProducts(data.items))
      .catch(() => {});
  }, [navigate, searchQuery, selectedCategory, token]);

  const filteredProducts = products.filter(product => {
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         product.brand.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         product.specs.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || product.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const addToCart = async (product: Product) => {
    if (!token) return;
    try {
      const resp = await checkInventoryAPI([{ product_id: product.id, quantity: 1 }], token);
      if (resp && resp.error) { window.alert(resp.error); return; }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Số lượng trong kho không đủ";
      window.alert(message);
      return;
    }

    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.id === product.id);
      if (existingItem) {
        return prevCart.map(item => item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item);
      }
      return [...prevCart, { ...product, quantity: 1 }];
    });

    try {
      await apiRequest("/customer/cart/add", {
        method: "POST", token,
        body: { product_id: product.id, name: product.name, category: product.category, price: product.price, quantity: 1, image: product.image, brand: product.brand, specs: product.specs },
      });
    } catch {}
  };

  const getCustomerIdFromToken = (): string => {
    if (!token) return "guest";
    try {
      const parts = token.split(".");
      if (parts.length < 2) return "guest";
      const payload = JSON.parse(atob(parts[1]));
      return String(payload.sub || "guest");
    } catch {
      return "guest";
    }
  };

  const sendChat = async () => {
    const message = chatInput.trim();
    if (!message || !token || isSendingChat) return;

    setIsSendingChat(true);
    setChatMessages((prev) => [...prev, { role: "user", content: message }]);
    setChatInput("");

    try {
      const result = await apiRequest<ChatApiResponse>("/ai/chat", {
        method: "POST",
        token,
        body: {
          message,
          user_id: getCustomerIdFromToken(),
        },
      });

      let assistantReply = "Da nhan yeu cau.";
      const suggestions = Array.isArray(result.products)
        ? result.products
            .filter((p): p is Partial<Product> & { id: string; name: string } => Boolean(p?.id && p?.name))
            .map((p) => ({
              id: String(p.id),
              name: String(p.name),
              category: p.category === "mobile" || p.category === "pc" ? p.category : "laptop",
              price: Number(p.price ?? 0),
              brand: String(p.brand ?? ""),
              specs: String(p.specs ?? ""),
              stock: Number(p.stock ?? 0),
              image: String(p.image ?? ""),
            }))
        : [];

      setChatSuggestions(suggestions);

      if (result.response) {
        assistantReply = result.response;
      } else if (result.message) {
        assistantReply = result.message;
      }

      if (!suggestions.length) {
        assistantReply = `${assistantReply} Vui long mo ta ro hon (vi du: laptop gaming 25 trieu, mobile pin trau duoi 15 trieu).`;
      }

      setChatMessages((prev) => [...prev, { role: "assistant", content: assistantReply }]);
    } catch (error) {
      const messageText = error instanceof Error ? error.message : "Chat bi loi";
      setChatMessages((prev) => [...prev, { role: "assistant", content: messageText }]);
    } finally {
      setIsSendingChat(false);
    }
  };

  const buySuggestedProduct = async (product: Product) => {
    await addToCart(product);
    setChatMessages((prev) => [
      ...prev,
      { role: "assistant", content: `Da them ${product.name} (${product.id}) vao gio hang.` },
    ]);
  };

  const updateQuantity = (productId: string, delta: number) => {
    setCart(prevCart =>
      prevCart.map(item => {
        if (item.id === productId) {
          const newQuantity = item.quantity + delta;
          return newQuantity > 0 ? { ...item, quantity: newQuantity } : item;
        }
        return item;
      }).filter(item => item.quantity > 0)
    );
  };

  const removeFromCart = (productId: string) => {
    setCart(prevCart => prevCart.filter(item => item.id !== productId));
  };

  // Step 1: place order + payment → go to shipping form
  const handleCheckout = async () => {
    if (cart.length === 0 || !token) return;
    setIsCheckingOut(true);
    try {
      const orderItems = cart.map(item => ({ product_id: item.id, quantity: item.quantity }));
      const currentTotal = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
      const currentCount = cart.reduce((sum, item) => sum + item.quantity, 0);
      const currentItems = [...cart];

      const orderResult = await createOrderAPI(orderItems, currentTotal, token);
      if (orderResult && orderResult.id && orderResult.transaction_id) {
        await processPaymentAPI(orderResult.id, orderResult.transaction_id, currentTotal, token);
      }

      setCart([]);
      try { await apiRequest("/customer/cart/clear", { method: "POST", token }); } catch {}

      const categoryParam = selectedCategory === "all" ? "all" : selectedCategory;
      try {
        const refreshed = await apiRequest<{ items: Product[] }>(`/catalog/search?q=${encodeURIComponent(searchQuery)}&category=${categoryParam}`, { token });
        setProducts(refreshed.items);
      } catch {}

      setOrderSummary({ totalAmount: currentTotal, itemCount: currentCount, items: currentItems });
      setFlowStep('shipping');
    } catch (error) {
      const message = error instanceof Error ? error.message : "Đặt hàng / Thanh toán thất bại";
      window.alert(message);
    } finally {
      setIsCheckingOut(false);
    }
  };

  // Step 2: validate + submit shipping info → done
  const validateShipping = (): boolean => {
    const errs: Partial<Record<keyof ShippingInfo, string>> = {};
    if (!shipping.fullName.trim()) errs.fullName = "Vui lòng nhập họ tên";
    if (!shipping.phone.trim()) errs.phone = "Vui lòng nhập số điện thoại";
    else if (!/^(0|\+84)[0-9]{8,10}$/.test(shipping.phone.replace(/\s/g, ""))) errs.phone = "Số điện thoại không hợp lệ";
    if (!shipping.address.trim()) errs.address = "Vui lòng nhập địa chỉ";
    if (!shipping.district.trim()) errs.district = "Vui lòng nhập quận/huyện";
    setShippingErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmitShipping = (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateShipping()) return;
    setFlowStep('done');
  };

  const selectedShipping = SHIPPING_OPTIONS.find(o => o.value === shipping.shippingMethod)!;
  const totalAmount = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);
  const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);

  // ── SHIPPING FORM SCREEN ────────────────────────────────────
  if (flowStep === 'shipping') {
    return (
      <div className="min-h-screen bg-slate-50 page-enter">
        <header className="bg-white shadow-sm sticky top-0 z-10">
          <div className="max-w-6xl mx-auto px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <ShoppingCart className="w-7 h-7 text-blue-500" />
                <h1 className="text-xl font-bold">Cửa Hàng Điện Tử</h1>
                {getUserName() && (
                  <span className="hidden sm:inline text-sm text-slate-500">
                    Xin chào, <span className="font-medium text-slate-700">{getUserName()}</span>
                  </span>
                )}
              </div>
              <div className="flex items-center gap-4">
                <Link to="/customer/login">
                  <Button variant="ghost" onClick={clearAuth}>
                    <LogOut className="w-5 h-5 mr-2" />
                    Đăng Xuất
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-6xl mx-auto px-4 py-8 flex flex-col items-center">
          <div className="w-full max-w-2xl pt-4">
          {/* progress */}
          <div className="flex items-center justify-center gap-3 mb-8">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center text-sm font-bold">✓</div>
              <span className="text-sm font-medium text-emerald-600">Thanh toán</span>
            </div>
            <div className="flex-1 h-0.5 bg-blue-300 max-w-16" />
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold">2</div>
              <span className="text-sm font-semibold text-blue-700">Thông tin giao hàng</span>
            </div>
            <div className="flex-1 h-0.5 bg-gray-200 max-w-16" />
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-gray-200 text-gray-500 flex items-center justify-center text-sm font-bold">3</div>
              <span className="text-sm text-gray-400">Hoàn tất</span>
            </div>
          </div>

          <Card className="shadow-xl border-0">
            <CardHeader className="bg-linear-to-r from-blue-600 to-indigo-600 text-white rounded-t-xl pb-6">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-white/20 rounded-lg">
                  <MapPin className="w-6 h-6" />
                </div>
                <div>
                  <CardTitle className="text-xl text-white">Thông Tin Giao Hàng</CardTitle>
                  <CardDescription className="text-blue-100">Điền địa chỉ nhận hàng của bạn</CardDescription>
                </div>
              </div>
            </CardHeader>

            <CardContent className="p-6">
              <form onSubmit={handleSubmitShipping} className="space-y-5">
                {/* Name + Email */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <Label htmlFor="s-name">Họ và tên <span className="text-red-500">*</span></Label>
                    <Input
                      id="s-name"
                      value={shipping.fullName}
                      onChange={e => setShipping(p => ({ ...p, fullName: e.target.value }))}
                      placeholder="Nguyễn Văn A"
                      className={shippingErrors.fullName ? "border-red-400" : ""}
                    />
                    {shippingErrors.fullName && <p className="text-xs text-red-500">{shippingErrors.fullName}</p>}
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="s-email">Email</Label>
                    <Input
                      id="s-email"
                      type="email"
                      value={shipping.email}
                      onChange={e => setShipping(p => ({ ...p, email: e.target.value }))}
                      placeholder="example@email.com"
                    />
                  </div>
                </div>

                {/* Phone */}
                <div className="space-y-1.5">
                  <Label htmlFor="s-phone">Số điện thoại <span className="text-red-500">*</span></Label>
                  <Input
                    id="s-phone"
                    type="tel"
                    value={shipping.phone}
                    onChange={e => setShipping(p => ({ ...p, phone: e.target.value }))}
                    placeholder="0912 345 678"
                    className={shippingErrors.phone ? "border-red-400" : ""}
                  />
                  {shippingErrors.phone && <p className="text-xs text-red-500">{shippingErrors.phone}</p>}
                </div>

                {/* Address */}
                <div className="space-y-1.5">
                  <Label htmlFor="s-address">Địa chỉ (số nhà, tên đường) <span className="text-red-500">*</span></Label>
                  <Input
                    id="s-address"
                    value={shipping.address}
                    onChange={e => setShipping(p => ({ ...p, address: e.target.value }))}
                    placeholder="123 Đường Lý Thường Kiệt"
                    className={shippingErrors.address ? "border-red-400" : ""}
                  />
                  {shippingErrors.address && <p className="text-xs text-red-500">{shippingErrors.address}</p>}
                </div>

                {/* District + City */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <Label htmlFor="s-district">Quận / Huyện <span className="text-red-500">*</span></Label>
                    <Input
                      id="s-district"
                      value={shipping.district}
                      onChange={e => setShipping(p => ({ ...p, district: e.target.value }))}
                      placeholder="Quận 1"
                      className={shippingErrors.district ? "border-red-400" : ""}
                    />
                    {shippingErrors.district && <p className="text-xs text-red-500">{shippingErrors.district}</p>}
                  </div>
                  <div className="space-y-1.5">
                    <Label htmlFor="s-city">Tỉnh / Thành phố</Label>
                    <Select value={shipping.city} onValueChange={v => setShipping(p => ({ ...p, city: v }))}>
                      <SelectTrigger id="s-city">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="TP. Hồ Chí Minh">TP. Hồ Chí Minh</SelectItem>
                        <SelectItem value="Hà Nội">Hà Nội</SelectItem>
                        <SelectItem value="Đà Nẵng">Đà Nẵng</SelectItem>
                        <SelectItem value="Cần Thơ">Cần Thơ</SelectItem>
                        <SelectItem value="Hải Phòng">Hải Phòng</SelectItem>
                        <SelectItem value="Nha Trang">Nha Trang</SelectItem>
                        <SelectItem value="Khác">Khác</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                {/* Shipping method */}
                <div className="space-y-2">
                  <Label>Hình thức vận chuyển <span className="text-red-500">*</span></Label>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    {SHIPPING_OPTIONS.map(opt => (
                      <button
                        key={opt.value}
                        type="button"
                        onClick={() => setShipping(p => ({ ...p, shippingMethod: opt.value }))}
                        className={`p-3 rounded-xl border-2 text-left transition-all ${
                          shipping.shippingMethod === opt.value
                            ? "border-blue-500 bg-blue-50"
                            : "border-gray-200 hover:border-blue-200"
                        }`}
                      >
                        <div className="text-2xl mb-1">{opt.icon}</div>
                        <div className="font-semibold text-sm">{opt.label}</div>
                        <div className="text-xs text-gray-500">{opt.desc}</div>
                        <div className="text-sm font-bold text-blue-600 mt-1">
                          {opt.price.toLocaleString('vi-VN')} ₫
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Note */}
                <div className="space-y-1.5">
                  <Label htmlFor="s-note">Ghi chú cho đơn hàng</Label>
                  <Input
                    id="s-note"
                    value={shipping.note}
                    onChange={e => setShipping(p => ({ ...p, note: e.target.value }))}
                    placeholder="VD: Giao giờ hành chính, gọi trước khi giao..."
                  />
                </div>

                {/* Order summary */}
                <div className="rounded-xl bg-slate-50 border border-slate-200 p-4 space-y-2">
                  <p className="text-sm font-semibold text-slate-700 mb-2">📋 Tóm tắt đơn hàng</p>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500">Sản phẩm ({orderSummary.itemCount} món)</span>
                    <span className="font-medium">{orderSummary.totalAmount.toLocaleString('vi-VN')} ₫</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500">Phí vận chuyển ({selectedShipping.label})</span>
                    <span className="font-medium">{selectedShipping.price.toLocaleString('vi-VN')} ₫</span>
                  </div>
                  <div className="border-t border-slate-200 pt-2 flex justify-between font-bold text-base">
                    <span>Tổng cộng</span>
                    <span className="text-blue-600">
                      {(orderSummary.totalAmount + selectedShipping.price).toLocaleString('vi-VN')} ₫
                    </span>
                  </div>
                </div>

                <Button type="submit" size="lg" className="w-full bg-blue-600 hover:bg-blue-700">
                  <Truck className="w-5 h-5 mr-2" />
                  Xác Nhận Thông Tin Giao Hàng
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
        </main>
      </div>
    );
  }

  // ── ORDER COMPLETE SCREEN ───────────────────────────────────
  if (flowStep === 'done') {
    return (
      <div className="min-h-screen bg-slate-50 page-enter">
        <header className="bg-white shadow-sm sticky top-0 z-10">
          <div className="max-w-6xl mx-auto px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <ShoppingCart className="w-7 h-7 text-blue-500" />
                <h1 className="text-xl font-bold">Cửa Hàng Điện Tử</h1>
                {getUserName() && (
                  <span className="hidden sm:inline text-sm text-slate-500">
                    Xin chào, <span className="font-medium text-slate-700">{getUserName()}</span>
                  </span>
                )}
              </div>
              <div className="flex items-center gap-4">
                <Link to="/customer/login">
                  <Button variant="ghost" onClick={clearAuth}>
                    <LogOut className="w-5 h-5 mr-2" />
                    Đăng Xuất
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-6xl mx-auto px-4 py-8 flex flex-col items-center">
        <div className="w-full max-w-lg pt-4">
          {/* progress */}
          <div className="flex items-center justify-center gap-3 mb-8">
            {[1, 2, 3].map((step, idx) => (
              <div key={step} className="flex items-center gap-2">
                {idx > 0 && <div className="flex-1 h-0.5 bg-emerald-400 max-w-16" />}
                <div className="w-8 h-8 rounded-full bg-emerald-500 text-white flex items-center justify-center text-sm font-bold">✓</div>
              </div>
            ))}
          </div>

          <Card className="shadow-2xl border-0 overflow-hidden">
            <div className="bg-linear-to-r from-emerald-500 to-teal-500 p-8 text-center text-white">
              <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle2 className="w-12 h-12 text-white" />
              </div>
              <h2 className="text-2xl font-bold mb-1">Đặt Hàng Thành Công!</h2>
              <p className="text-emerald-100">Cảm ơn bạn đã mua hàng tại cửa hàng chúng tôi</p>
            </div>

            <CardContent className="p-6 space-y-4">
              {/* Shipping address recap */}
              <div className="rounded-xl bg-blue-50 border border-blue-100 p-4 space-y-1">
                <p className="text-sm font-semibold text-blue-700 flex items-center gap-2 mb-2">
                  <MapPin className="w-4 h-4" /> Địa chỉ giao hàng
                </p>
                <p className="font-semibold">{shipping.fullName}</p>
                {shipping.phone && <p className="text-sm text-slate-600">📞 {shipping.phone}</p>}
                {shipping.email && <p className="text-sm text-slate-600">✉️ {shipping.email}</p>}
                <p className="text-sm text-slate-600">{shipping.address}, {shipping.district}, {shipping.city}</p>
                {shipping.note && <p className="text-sm text-slate-500 italic">📝 {shipping.note}</p>}
              </div>

              {/* Order items */}
              <div className="rounded-xl bg-slate-50 border border-slate-200 p-4 space-y-2">
                <p className="text-sm font-semibold text-slate-700 mb-2 flex items-center gap-2">
                  <Package className="w-4 h-4" /> Sản phẩm đã đặt
                </p>
                {orderSummary.items.map(item => (
                  <div key={item.id} className="flex justify-between text-sm">
                    <span className="text-slate-600 truncate max-w-[60%]">{item.name} <span className="text-slate-400">x{item.quantity}</span></span>
                    <span className="font-medium">{(item.price * item.quantity).toLocaleString('vi-VN')} ₫</span>
                  </div>
                ))}
                <div className="border-t border-slate-200 pt-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-500">Phí ship ({selectedShipping.label})</span>
                    <span>{selectedShipping.price.toLocaleString('vi-VN')} ₫</span>
                  </div>
                </div>
                <div className="flex justify-between font-bold pt-1">
                  <span>Tổng thanh toán</span>
                  <span className="text-blue-600 text-lg">
                    {(orderSummary.totalAmount + selectedShipping.price).toLocaleString('vi-VN')} ₫
                  </span>
                </div>
              </div>

              {/* Shipping badge */}
              <div className="flex items-center gap-3 rounded-xl bg-amber-50 border border-amber-200 p-3">
                <span className="text-2xl">{selectedShipping.icon}</span>
                <div>
                  <p className="font-semibold text-sm">{selectedShipping.label}</p>
                  <p className="text-xs text-amber-700">Dự kiến: {selectedShipping.desc}</p>
                </div>
                <Badge className="ml-auto bg-amber-100 text-amber-800 hover:bg-amber-100">
                  Đang xử lý
                </Badge>
              </div>

              <Button
                size="lg"
                className="w-full bg-emerald-600 hover:bg-emerald-700 mt-2"
                onClick={() => setFlowStep('shop')}
              >
                Tiếp tục mua sắm
              </Button>
            </CardContent>
          </Card>
        </div>

        </main>
      </div>
    );
  }

  // ── MAIN SHOP SCREEN ────────────────────────────────────────
  return (
    <div className="min-h-screen bg-slate-50 page-enter">
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <ShoppingCart className="w-7 h-7 text-blue-500" />
              <h1 className="text-xl font-bold">Cửa Hàng Điện Tử</h1>
              {getUserName() && (
                <span className="hidden sm:inline text-sm text-slate-500">
                  Xin chào, <span className="font-medium text-slate-700">{getUserName()}</span>
                </span>
              )}
            </div>

            <div className="flex items-center gap-4">
              <Sheet>
                <SheetTrigger asChild>
                  <Button variant="outline" className="relative btn-press">
                    <ShoppingCart className="w-5 h-5 mr-2" />
                    Giỏ Hàng
                    {totalItems > 0 && (
                      <Badge className="ml-2 bg-red-500">{totalItems}</Badge>
                    )}
                  </Button>
                </SheetTrigger>
                <SheetContent className="w-full sm:max-w-md p-0 flex flex-col">
                  <SheetHeader className="px-4 py-3 border-b">
                    <SheetTitle>Giỏ Hàng của Bạn</SheetTitle>
                  </SheetHeader>
                  <div className="px-4 py-3 space-y-3 flex-1 overflow-y-auto">
                    {cart.length === 0 ? (
                      <p className="text-center text-gray-500 py-8">Giỏ hàng trống</p>
                    ) : (
                      <>
                        <div className="space-y-3">
                          {cart.map(item => (
                            <Card key={item.id} className="reveal-up" style={{ animationDelay: '40ms' }}>
                              <CardContent className="p-3">
                                <div className="flex gap-3">
                                  <img src={item.image} alt={item.name} className="w-14 h-14 object-cover rounded" />
                                  <div className="flex-1">
                                    <h3 className="font-semibold text-sm leading-tight line-clamp-2">{item.name}</h3>
                                    <p className="text-xs text-gray-500">{item.brand}</p>
                                    <p className="text-blue-600 font-semibold text-sm">
                                      {item.price.toLocaleString('vi-VN')} ₫
                                    </p>
                                  </div>
                                </div>
                                <div className="flex items-center justify-between mt-3">
                                  <div className="flex items-center gap-1.5">
                                    <Button size="sm" variant="outline" onClick={() => updateQuantity(item.id, -1)} className="h-7 w-7 px-0">
                                      <Minus className="w-4 h-4" />
                                    </Button>
                                    <span className="w-7 text-center text-sm">{item.quantity}</span>
                                    <Button size="sm" variant="outline" onClick={() => updateQuantity(item.id, 1)} className="h-7 w-7 px-0">
                                      <Plus className="w-4 h-4" />
                                    </Button>
                                  </div>
                                  <Button size="sm" variant="destructive" onClick={() => removeFromCart(item.id)} className="h-7 w-7 px-0">
                                    <Trash2 className="w-4 h-4" />
                                  </Button>
                                </div>
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                        <div className="border-t pt-3 bg-white sticky bottom-0 pb-2">
                          <div className="flex justify-between items-center mb-4">
                            <span className="text-base font-semibold">Tổng cộng:</span>
                            <span className="text-3xl font-bold text-blue-600">
                              {totalAmount.toLocaleString('vi-VN')} ₫
                            </span>
                          </div>
                          <Button
                            className="w-full btn-press" size="lg"
                            onClick={handleCheckout}
                            disabled={isCheckingOut || cart.length === 0}
                          >
                            {isCheckingOut ? "Đang xử lý..." : "Xác nhận & Thanh toán"}
                          </Button>
                        </div>
                      </>
                    )}
                  </div>
                </SheetContent>
              </Sheet>

              <Link to="/customer/login">
                <Button variant="ghost" onClick={clearAuth}>
                  <LogOut className="w-5 h-5 mr-2" />
                  Đăng Xuất
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-6">
        {/* Search */}
        <div className="mb-5">
          <div className="relative max-w-2xl">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <Input
              type="text"
              placeholder="Tìm kiếm sản phẩm theo tên, thương hiệu, cấu hình..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 h-10"
            />
          </div>
        </div>

        <Card className="mb-5">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <MessageCircle className="w-5 h-5 text-blue-600" />
              AI Assistant
            </CardTitle>
            <CardDescription>AI chi goi y san pham co san trong he thong. Ban bam "Mua goi y" de them vao gio.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="rounded-md border h-44 overflow-y-auto p-3 bg-slate-50 space-y-2">
              {chatMessages.length === 0 ? (
                <p className="text-sm text-slate-500">Hay thu: "laptop gaming 30 trieu", "mobile samsung duoi 20 trieu", "laptop do hoa 2K"</p>
              ) : (
                chatMessages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`text-sm p-2 rounded-md ${msg.role === "user" ? "bg-blue-100" : "bg-white border"}`}
                  >
                    <span className="font-semibold mr-1">{msg.role === "user" ? "Ban:" : "AI:"}</span>
                    <span>{msg.content}</span>
                  </div>
                ))
              )}
            </div>

            <div className="mt-3 flex gap-2">
              <Input
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Nhap noi dung chat..."
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    sendChat();
                  }
                }}
              />
              <Button onClick={sendChat} disabled={isSendingChat || !chatInput.trim()}>
                <Send className="w-4 h-4 mr-1" />
                Gui
              </Button>
            </div>

            <div className="mt-4 rounded-xl border border-slate-200 overflow-hidden bg-white">
              <div className="px-3 py-2 border-b bg-slate-100 flex items-center gap-2 text-sm font-semibold text-slate-700">
                <Sparkles className="w-4 h-4 text-blue-600" />
                Bang goi y mua nhanh
              </div>

              {chatSuggestions.length === 0 ? (
                <div className="px-3 py-6 text-sm text-slate-500">Chua co goi y. Hay nhap nhu cau de AI tra ve danh sach san pham tu database.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-slate-50 text-slate-600">
                      <tr>
                        <th className="text-left px-3 py-2">Ma</th>
                        <th className="text-left px-3 py-2">San pham</th>
                        <th className="text-left px-3 py-2">Loai</th>
                        <th className="text-right px-3 py-2">Gia</th>
                        <th className="text-right px-3 py-2">Ton</th>
                        <th className="text-right px-3 py-2">Mua</th>
                      </tr>
                    </thead>
                    <tbody>
                      {chatSuggestions.map((item) => (
                        <tr key={item.id} className="border-t">
                          <td className="px-3 py-2 font-medium">{item.id}</td>
                          <td className="px-3 py-2">
                            <div className="font-medium text-slate-800">{item.name}</div>
                            <div className="text-xs text-slate-500">{item.brand}</div>
                          </td>
                          <td className="px-3 py-2">
                            {item.category === "laptop" ? "Laptop" : item.category === "mobile" ? "Mobile" : "PC"}
                          </td>
                          <td className="px-3 py-2 text-right font-semibold text-blue-600">{item.price.toLocaleString("vi-VN")} ₫</td>
                          <td className="px-3 py-2 text-right">{item.stock}</td>
                          <td className="px-3 py-2 text-right">
                            <Button
                              size="sm"
                              className="h-8"
                              onClick={() => buySuggestedProduct(item)}
                              disabled={item.stock <= 0}
                            >
                              Mua goi y
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Category Tabs */}
        <Tabs value={selectedCategory} onValueChange={(v) => setSelectedCategory(v as any)} className="mb-5">
          <TabsList>
            <TabsTrigger value="all">Tất Cả</TabsTrigger>
            <TabsTrigger value="laptop">
              <Laptop className="w-4 h-4 mr-2" />Laptop
            </TabsTrigger>
            <TabsTrigger value="mobile">
              <Smartphone className="w-4 h-4 mr-2" />Mobile
            </TabsTrigger>
            <TabsTrigger value="pc">
              <Monitor className="w-4 h-4 mr-2" />PC
            </TabsTrigger>
          </TabsList>

          <TabsContent value={selectedCategory} className="mt-4">
            {filteredProducts.length === 0 ? (
              <Card>
                <CardContent className="py-12 text-center">
                  <p className="text-gray-500">Không tìm thấy sản phẩm nào</p>
                </CardContent>
              </Card>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredProducts.map((product, index) => (
                  <Card key={product.id} className="card-lift reveal-up" style={{ animationDelay: `${index * 45}ms` }}>
                    <CardHeader className="p-4 pb-2">
                      <img src={product.image} alt={product.name} className="w-full h-36 object-cover rounded-lg mb-3" />
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-base leading-tight line-clamp-2">{product.name}</CardTitle>
                          <CardDescription className="text-xs">{product.brand}</CardDescription>
                        </div>
                        <Badge variant={product.category === 'laptop' ? 'default' : 'secondary'}>
                          {product.category === 'laptop' ? (
                            <Laptop className="w-3 h-3" />
                          ) : product.category === 'mobile' ? (
                            <Smartphone className="w-3 h-3" />
                          ) : (
                            <Monitor className="w-3 h-3" />
                          )}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="p-4 pt-0">
                      <p className="text-sm text-gray-600 mb-3 line-clamp-2">{product.specs}</p>
                      <div className="flex items-center justify-between mb-3">
                        <span className="text-4xl font-bold text-blue-600 leading-none">
                          {product.price.toLocaleString('vi-VN')} ₫
                        </span>
                        <Badge variant="outline">Kho: {product.stock}</Badge>
                      </div>
                      <Button
                        className="w-full h-9 btn-press"
                        onClick={() => addToCart(product)}
                        disabled={product.stock === 0}
                      >
                        <ShoppingCart className="w-4 h-4 mr-2" />
                        Thêm Vào Giỏ
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}
