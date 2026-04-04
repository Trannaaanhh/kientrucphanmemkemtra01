import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import { UserCog, LogOut, Plus, Edit, Trash2, Laptop, Smartphone, Monitor, MessageSquare } from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "../components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../components/ui/alert-dialog";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "../components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { mockProducts, type Product } from "../data/mockData";
import { apiRequest, clearAuth, getAuthRole, getAuthToken, getUserName } from "../services/api";
import { getInventoryAPI, getOrdersAPI, getPaymentsAPI, updateInventoryAPI } from "../services/microservices";

interface ChatHistoryItem {
  timestamp: string;
  role: "user" | "assistant";
  content: string;
  metadata?: Record<string, unknown>;
}

interface ChatSession {
  user_id: string;
  message_count: number;
  last_message: ChatHistoryItem | null;
  history: ChatHistoryItem[];
}

export function StaffDashboard() {
  const navigate = useNavigate();
  const [products, setProducts] = useState<Product[]>(mockProducts);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [deletingProductId, setDeletingProductId] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<'all' | 'laptop' | 'mobile' | 'pc'>('all');

  const [currentTab, setCurrentTab] = useState<'products' | 'inventory' | 'orders' | 'payments' | 'chat'>('products');
  const [inventory, setInventory] = useState<any[]>([]);
  const [orders, setOrders] = useState<any[]>([]);
  const [payments, setPayments] = useState<any[]>([]);
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);

  useEffect(() => {
    const role = getAuthRole();
    if (role !== "staff" || !getAuthToken()) {
      clearAuth();
      navigate("/staff/login");
    }
  }, [navigate]);

  useEffect(() => {
    const token = getAuthToken();
    if (!token) return;

    const loadProducts = async () => {
      try {
        const data = await apiRequest<{ items: Product[] }>("/staff/products", {
          method: "GET",
          token,
        });
        if (Array.isArray(data.items) && data.items.length > 0) {
          setProducts(data.items);
        }
      } catch {
        // Keep local mock products when API is unavailable.
      }
    };

    loadProducts();
  }, []);

  useEffect(() => {
    const token = getAuthToken();
    if (!token) return;

    if (currentTab === 'inventory') {
      // Auto-sync
      const items = products.map(p => ({ product_id: p.id, quantity: p.stock }));
      updateInventoryAPI(items, token)
        .then(() => getInventoryAPI(token))
        .then(setInventory)
        .catch(console.error);
    } else if (currentTab === 'orders') {
      getOrdersAPI(token).then(setOrders).catch(console.error);
    } else if (currentTab === 'payments') {
      getPaymentsAPI(token).then(setPayments).catch(console.error);
    } else if (currentTab === 'chat') {
      apiRequest<{ sessions: ChatSession[] }>("/ai/history", { token })
        .then((data) => setChatSessions(data.sessions || []))
        .catch(console.error);
    }
  }, [currentTab, products]);

  const [formData, setFormData] = useState({
    name: '',
    category: 'laptop' as 'laptop' | 'mobile' | 'pc',
    price: '',
    brand: '',
    specs: '',
    stock: '',
    image: ''
  });

  const resetForm = () => {
    setFormData({
      name: '',
      category: 'laptop',
      price: '',
      brand: '',
      specs: '',
      stock: '',
      image: ''
    });
  };

  const normalizeImageInput = (value: string) => {
    const raw = value.trim();
    if (!raw) return "";
    if (raw.startsWith("http://") || raw.startsWith("https://") || raw.startsWith("/assets/")) {
      return raw;
    }

    const filename = raw.split(/[\\/]/).pop() || raw;
    return `/assets/${filename}`;
  };

  const resolveImagePathForSave = async (
    imageValue: string,
    productName: string,
    category: 'laptop' | 'mobile' | 'pc',
  ) => {
    const normalized = normalizeImageInput(imageValue);
    if (!normalized) {
      return 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400';
    }

    if (normalized.startsWith('http://') || normalized.startsWith('https://')) {
      const token = getAuthToken();
      if (!token) {
        throw new Error('Missing auth token');
      }

      const imported = await apiRequest<{ image: string }>('/staff/assets/import', {
        method: 'POST',
        token,
        body: {
          image_url: normalized,
          name: productName,
          category,
        },
      });
      return imported.image;
    }

    return normalized;
  };

  const handleAddProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    let resolvedImage = '';
    try {
      resolvedImage = await resolveImagePathForSave(formData.image, formData.name, formData.category);
    } catch {
      window.alert('Không thể tải ảnh từ link vào assets. Vui lòng kiểm tra lại URL hình ảnh.');
      return;
    }

    const newProduct = {
      name: formData.name,
      category: formData.category,
      price: Number(formData.price),
      brand: formData.brand,
      specs: formData.specs,
      stock: Number(formData.stock),
      image: resolvedImage,
    };

    const token = getAuthToken();
    if (token) {
      try {
        const created = await apiRequest<Product>("/staff/products", {
          method: "POST",
          token,
          body: newProduct,
        });
        setProducts((prev) => [...prev, created]);
      } catch {
        // Keep local optimistic update when API is unavailable.
        const fallbackProduct: Product = {
          id: `${formData.category === 'laptop' ? 'L' : formData.category === 'mobile' ? 'M' : 'PC'}${String(products.length + 1).padStart(3, '0')}`,
          ...newProduct,
        };
        setProducts((prev) => [...prev, fallbackProduct]);
      }
    } else {
      const fallbackProduct: Product = {
        id: `${formData.category === 'laptop' ? 'L' : formData.category === 'mobile' ? 'M' : 'PC'}${String(products.length + 1).padStart(3, '0')}`,
        ...newProduct,
      };
      setProducts((prev) => [...prev, fallbackProduct]);
    }

    setIsAddDialogOpen(false);
    resetForm();
  };

  const handleEditProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!editingProduct) return;

    let resolvedImage = '';
    try {
      resolvedImage = await resolveImagePathForSave(formData.image, formData.name, formData.category);
    } catch {
      window.alert('Không thể tải ảnh từ link vào assets. Vui lòng kiểm tra lại URL hình ảnh.');
      return;
    }

    setProducts(products.map(p => 
      p.id === editingProduct.id
        ? {
            ...p,
            name: formData.name,
            category: formData.category,
            price: Number(formData.price),
            brand: formData.brand,
            specs: formData.specs,
            stock: Number(formData.stock),
            image: resolvedImage
          }
        : p
    ));

    const token = getAuthToken();
    if (token) {
      try {
        await apiRequest(`/staff/products/${editingProduct.id}`, {
          method: "PUT",
          token,
          body: {
            name: formData.name,
            category: formData.category,
            price: Number(formData.price),
            brand: formData.brand,
            specs: formData.specs,
            stock: Number(formData.stock),
            image: resolvedImage,
          },
        });
      } catch {
        // Keep local optimistic update when API is unavailable.
      }
    }

    setIsEditDialogOpen(false);
    setEditingProduct(null);
    resetForm();
  };

  const handleDeleteProduct = (productId: string) => {
    setProducts(products.filter(p => p.id !== productId));
    setDeletingProductId(null);
  };

  const openEditDialog = (product: Product) => {
    setEditingProduct(product);
    setFormData({
      name: product.name,
      category: product.category,
      price: String(product.price),
      brand: product.brand,
      specs: product.specs,
      stock: String(product.stock),
      image: product.image
    });
    setIsEditDialogOpen(true);
  };

  const filteredProducts = selectedCategory === 'all'
    ? products
    : products.filter(p => p.category === selectedCategory);

  const laptopCount = products.filter(p => p.category === 'laptop').length;
  const mobileCount = products.filter(p => p.category === 'mobile').length;
  const pcCount = products.filter(p => p.category === 'pc').length;
  const totalStock = products.reduce((sum, p) => sum + p.stock, 0);

  return (
    <div className="min-h-screen bg-gray-50 page-enter">
      {/* Header */}
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <UserCog className="w-8 h-8 text-green-500" />
              <h1 className="text-2xl font-bold">Quản Lý Sản Phẩm</h1>
              {getUserName() && (
                <span className="hidden sm:inline text-sm text-slate-500">
                  Nhân viên: <span className="font-medium text-slate-700">{getUserName()}</span>
                </span>
              )}
            </div>

            <div className="flex items-center gap-4">
              <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
                <DialogTrigger asChild>
                  <Button onClick={resetForm} className="btn-press">
                    <Plus className="w-5 h-5 mr-2" />
                    Thêm Sản Phẩm
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>Thêm Sản Phẩm Mới</DialogTitle>
                    <DialogDescription>
                      Nhập thông tin sản phẩm mới vào hệ thống
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleAddProduct} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="name">Tên sản phẩm *</Label>
                        <Input
                          id="name"
                          value={formData.name}
                          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="category">Danh mục *</Label>
                        <Select
                          value={formData.category}
                          onValueChange={(value: 'laptop' | 'mobile' | 'pc') =>
                            setFormData({ ...formData, category: value })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="laptop">Laptop</SelectItem>
                            <SelectItem value="mobile">Mobile</SelectItem>
                            <SelectItem value="pc">PC</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="brand">Thương hiệu *</Label>
                        <Input
                          id="brand"
                          value={formData.brand}
                          onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="price">Giá (VNĐ) *</Label>
                        <Input
                          id="price"
                          type="number"
                          value={formData.price}
                          onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                          required
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="specs">Cấu hình *</Label>
                      <Input
                        id="specs"
                        value={formData.specs}
                        onChange={(e) => setFormData({ ...formData, specs: e.target.value })}
                        placeholder="VD: Intel Core i7, 16GB RAM, 512GB SSD"
                        required
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="stock">Số lượng kho *</Label>
                        <Input
                          id="stock"
                          type="number"
                          value={formData.stock}
                          onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
                          required
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="image">Đường dẫn hình ảnh</Label>
                        <Input
                          id="image"
                          type="text"
                          value={formData.image}
                          onChange={(e) => setFormData({ ...formData, image: e.target.value })}
                          placeholder="VD: laptop-asus-rog-strix-scar-18-g835lw-sa172w.png hoặc /assets/..."
                        />
                      </div>
                    </div>

                    <div className="flex justify-end gap-2">
                      <Button type="button" variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                        Hủy
                      </Button>
                      <Button type="submit">Thêm Sản Phẩm</Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>

              <Link to="/staff/login">
                <Button variant="ghost" onClick={clearAuth} className="btn-press">
                  <LogOut className="w-5 h-5 mr-2" />
                  Đăng Xuất
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <Tabs value={currentTab} onValueChange={(v) => setCurrentTab(v as any)} className="mb-8">
          <TabsList className="grid grid-cols-5 max-w-3xl bg-white shadow-sm rounded-lg p-1 border">
            <TabsTrigger value="products">Sản Phẩm</TabsTrigger>
            <TabsTrigger value="inventory">Kho Hàng</TabsTrigger>
            <TabsTrigger value="orders">Đơn Phẩm</TabsTrigger>
            <TabsTrigger value="payments">Thanh Toán</TabsTrigger>
            <TabsTrigger value="chat">Chat KH</TabsTrigger>
          </TabsList>
        </Tabs>

        {currentTab === 'products' && (
          <div>
            {/* Statistics */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="card-lift reveal-up" style={{ animationDelay: '40ms' }}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Tổng Laptop</CardTitle>
              <Laptop className="h-4 w-4 text-gray-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{laptopCount}</div>
              <p className="text-xs text-gray-600">sản phẩm</p>
            </CardContent>
          </Card>
          <Card className="card-lift reveal-up" style={{ animationDelay: '90ms' }}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Tổng Mobile</CardTitle>
              <Smartphone className="h-4 w-4 text-gray-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{mobileCount}</div>
              <p className="text-xs text-gray-600">sản phẩm</p>
            </CardContent>
          </Card>
          <Card className="card-lift reveal-up" style={{ animationDelay: '140ms' }}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Tổng PC</CardTitle>
              <Monitor className="h-4 w-4 text-gray-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{pcCount}</div>
              <p className="text-xs text-gray-600">sản phẩm</p>
            </CardContent>
          </Card>
          <Card className="card-lift reveal-up" style={{ animationDelay: '180ms' }}>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">Tổng Kho</CardTitle>
              <UserCog className="h-4 w-4 text-gray-600" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{totalStock}</div>
              <p className="text-xs text-gray-600">sản phẩm</p>
            </CardContent>
          </Card>
        </div>

        {/* Products Table */}
        <Card className="reveal-up" style={{ animationDelay: '180ms' }}>
          <CardHeader>
            <CardTitle>Danh Sách Sản Phẩm</CardTitle>
            <CardDescription>Quản lý tất cả sản phẩm trong hệ thống</CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs value={selectedCategory} onValueChange={(v) => setSelectedCategory(v as any)}>
              <TabsList className="mb-4">
                <TabsTrigger value="all">Tất Cả ({products.length})</TabsTrigger>
                <TabsTrigger value="laptop">Laptop ({laptopCount})</TabsTrigger>
                <TabsTrigger value="mobile">Mobile ({mobileCount})</TabsTrigger>
                <TabsTrigger value="pc">PC ({pcCount})</TabsTrigger>
              </TabsList>

              <TabsContent value={selectedCategory}>
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>ID</TableHead>
                        <TableHead>Hình ảnh</TableHead>
                        <TableHead>Tên sản phẩm</TableHead>
                        <TableHead>Danh mục</TableHead>
                        <TableHead>Thương hiệu</TableHead>
                        <TableHead>Giá</TableHead>
                        <TableHead>Kho</TableHead>
                        <TableHead className="text-right">Thao tác</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {filteredProducts.map((product, index) => (
                        <TableRow key={product.id} className="reveal-up" style={{ animationDelay: `${220 + index * 26}ms` }}>
                          <TableCell className="font-medium">{product.id}</TableCell>
                          <TableCell>
                            <img src={product.image} alt={product.name} className="w-12 h-12 object-cover rounded" />
                          </TableCell>
                          <TableCell>
                            <div>
                              <div className="font-medium">{product.name}</div>
                              <div className="text-sm text-gray-500">{product.specs}</div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <Badge variant={product.category === 'laptop' ? 'default' : 'secondary'}>
                              {product.category === 'laptop' ? 'Laptop' : product.category === 'mobile' ? 'Mobile' : 'PC'}
                            </Badge>
                          </TableCell>
                          <TableCell>{product.brand}</TableCell>
                          <TableCell>{product.price.toLocaleString('vi-VN')} ₫</TableCell>
                          <TableCell>
                            <Badge variant={product.stock > 10 ? 'outline' : 'destructive'}>
                              {product.stock}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex justify-end gap-2">
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => openEditDialog(product)}
                                className="btn-press"
                              >
                                <Edit className="w-4 h-4" />
                              </Button>
                              <Button
                                size="sm"
                                variant="destructive"
                                onClick={() => setDeletingProductId(product.id)}
                                className="btn-press"
                              >
                                <Trash2 className="w-4 h-4" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
        </div>
        )}

        {currentTab === 'inventory' && (
          <Card className="reveal-up">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Quản Lý Kho Hàng</CardTitle>
                <CardDescription>Số lượng tồn kho được tự động đồng bộ liên tục</CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Mã SP</TableHead>
                    <TableHead>Tên Sản Phẩm</TableHead>
                    <TableHead>Danh Mục</TableHead>
                    <TableHead>Đơn Giá</TableHead>
                    <TableHead>Tồn Kho</TableHead>
                    <TableHead>Giá Trị Kho</TableHead>
                    <TableHead>Trạng Thái</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {inventory.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center text-gray-400 py-8">
                        Chưa có dữ liệu kho — nhấn "Đồng bộ từ Sản Phẩm" để tải
                      </TableCell>
                    </TableRow>
                  ) : (
                    inventory.map((inv: any, idx: number) => {
                      const product = products.find(p => p.id === inv.product_id);
                      const stockValue = product ? product.price * inv.quantity : 0;
                      return (
                        <TableRow key={idx}>
                          <TableCell className="font-mono text-xs">{inv.product_id}</TableCell>
                          <TableCell className="font-semibold">
                            {product ? product.name : <span className="text-gray-400 text-sm italic">Không rõ</span>}
                          </TableCell>
                          <TableCell>
                            {product ? (
                              <Badge variant={product.category === 'laptop' ? 'default' : 'secondary'}>
                                {product.category === 'laptop' ? 'Laptop' : product.category === 'mobile' ? 'Mobile' : 'PC'}
                              </Badge>
                            ) : '—'}
                          </TableCell>
                          <TableCell className="text-blue-700 font-medium">
                            {product ? product.price.toLocaleString('vi-VN') + ' ₫' : '—'}
                          </TableCell>
                          <TableCell>
                            <Badge variant={inv.quantity > 10 ? 'outline' : inv.quantity > 0 ? 'secondary' : 'destructive'}>
                              {inv.quantity}
                            </Badge>
                          </TableCell>
                          <TableCell className="font-medium">
                            {stockValue > 0 ? stockValue.toLocaleString('vi-VN') + ' ₫' : '—'}
                          </TableCell>
                          <TableCell>
                            {inv.quantity === 0 ? (
                              <Badge variant="destructive">Hết hàng</Badge>
                            ) : inv.quantity <= 5 ? (
                              <Badge variant="secondary" className="bg-orange-100 text-orange-700">Sắp hết</Badge>
                            ) : (
                              <Badge variant="outline" className="text-green-700 border-green-300">Còn hàng</Badge>
                            )}
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
              {inventory.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-6 text-sm text-gray-600 border-t pt-4">
                  <span>Tổng loại SP: <strong>{inventory.length}</strong></span>
                  <span>Tổng tồn kho: <strong>{inventory.reduce((s: number, i: any) => s + i.quantity, 0)}</strong> sản phẩm</span>
                  <span>Giá trị kho ≈ <strong className="text-blue-700">
                    {inventory.reduce((s: number, i: any) => {
                      const p = products.find((pr: any) => pr.id === i.product_id);
                      return s + (p ? p.price * i.quantity : 0);
                    }, 0).toLocaleString('vi-VN')} ₫
                  </strong></span>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {currentTab === 'orders' && (
          <Card className="reveal-up">
            <CardHeader>
              <CardTitle>Quản Lý Đơn Hàng</CardTitle>
              <CardDescription>Theo dõi các đơn hàng được tạo bằng order-service</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Khách Hàng</TableHead>
                    <TableHead>Tổng Tiền</TableHead>
                    <TableHead>Trạng Thái</TableHead>
                    <TableHead>Chi Tiết SP</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {orders.map((ord, idx) => (
                    <TableRow key={idx}>
                      <TableCell>{ord.id}</TableCell>
                      <TableCell>{ord.customer_id}</TableCell>
                      <TableCell>{Number(ord.total_amount).toLocaleString('vi-VN')} ₫</TableCell>
                      <TableCell>
                        <Badge variant={ord.status === 'PAID' ? 'default' : ord.status === 'CANCELLED' ? 'destructive' : 'secondary'}>
                          {ord.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          {ord.items?.map((i: any) => (
                            <div key={i.product_id}>{i.product_id} (x{i.quantity})</div>
                          ))}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {currentTab === 'payments' && (
          <Card className="reveal-up">
            <CardHeader>
              <CardTitle>Quản Lý Thanh Toán</CardTitle>
              <CardDescription>Theo dõi trạng thái giao dịch từ payment-service</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Mã Giao Dịch</TableHead>
                    <TableHead>Đơn Hàng ID</TableHead>
                    <TableHead>Số Tiền</TableHead>
                    <TableHead>Trạng Thái</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {payments.map((pay, idx) => (
                    <TableRow key={idx}>
                      <TableCell>{pay.id}</TableCell>
                      <TableCell className="text-xs text-gray-500">{pay.transaction_id}</TableCell>
                      <TableCell>{pay.order_id}</TableCell>
                      <TableCell>{Number(pay.amount).toLocaleString('vi-VN')} ₫</TableCell>
                      <TableCell>
                        <Badge variant={pay.status === 'SUCCESS' ? 'default' : 'destructive'}>
                          {pay.status}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {currentTab === 'chat' && (
          <Card className="reveal-up">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="w-5 h-5 text-blue-600" />
                  Lịch Sử Chat Khách Hàng
                </CardTitle>
                <CardDescription>Nhân viên theo dõi hội thoại customer với AI Assistant</CardDescription>
              </div>
              <Button
                variant="outline"
                onClick={async () => {
                  const token = getAuthToken();
                  if (!token) return;
                  const data = await apiRequest<{ sessions: ChatSession[] }>("/ai/history", { token });
                  setChatSessions(data.sessions || []);
                }}
              >
                Tải Lại
              </Button>
            </CardHeader>
            <CardContent className="space-y-4">
              {chatSessions.length === 0 ? (
                <p className="text-sm text-gray-500">Chưa có lịch sử chat nào từ customer.</p>
              ) : (
                chatSessions.map((session) => (
                  <div key={session.user_id} className="rounded-lg border p-4 bg-slate-50">
                    <div className="flex flex-wrap items-center gap-3 mb-3">
                      <Badge variant="outline">User: {session.user_id}</Badge>
                      <Badge>{session.message_count} tin nhan</Badge>
                      {session.last_message?.timestamp && (
                        <span className="text-xs text-gray-500">
                          Moi nhat: {new Date(session.last_message.timestamp).toLocaleString("vi-VN")}
                        </span>
                      )}
                    </div>

                    <div className="max-h-64 overflow-y-auto space-y-2">
                      {session.history.map((msg, idx) => (
                        <div
                          key={`${session.user_id}-${idx}`}
                          className={`rounded-md p-2 text-sm ${msg.role === "user" ? "bg-blue-100" : "bg-white border"}`}
                        >
                          <div className="font-semibold mb-1">{msg.role === "user" ? "Customer" : "AI"}</div>
                          <div>{msg.content}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              )}
            </CardContent>
          </Card>
        )}
      </main>

      {/* Edit Dialog */}
      <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Cập Nhật Sản Phẩm</DialogTitle>
            <DialogDescription>
              Chỉnh sửa thông tin sản phẩm
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleEditProduct} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-name">Tên sản phẩm *</Label>
                <Input
                  id="edit-name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-category">Danh mục *</Label>
                <Select
                  value={formData.category}
                  onValueChange={(value: 'laptop' | 'mobile' | 'pc') =>
                    setFormData({ ...formData, category: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="laptop">Laptop</SelectItem>
                    <SelectItem value="mobile">Mobile</SelectItem>
                    <SelectItem value="pc">PC</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-brand">Thương hiệu *</Label>
                <Input
                  id="edit-brand"
                  value={formData.brand}
                  onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-price">Giá (VNĐ) *</Label>
                <Input
                  id="edit-price"
                  type="number"
                  value={formData.price}
                  onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                  required
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-specs">Cấu hình *</Label>
              <Input
                id="edit-specs"
                value={formData.specs}
                onChange={(e) => setFormData({ ...formData, specs: e.target.value })}
                required
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-stock">Số lượng kho *</Label>
                <Input
                  id="edit-stock"
                  type="number"
                  value={formData.stock}
                  onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-image">Đường dẫn hình ảnh</Label>
                <Input
                  id="edit-image"
                  type="text"
                  value={formData.image}
                  onChange={(e) => setFormData({ ...formData, image: e.target.value })}
                  placeholder="VD: laptop-asus-rog-strix-scar-18-g835lw-sa172w.png hoặc /assets/..."
                />
              </div>
            </div>

            <div className="flex justify-end gap-2">
              <Button type="button" variant="outline" onClick={() => setIsEditDialogOpen(false)}>
                Hủy
              </Button>
              <Button type="submit">Cập Nhật</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      <AlertDialog open={Boolean(deletingProductId)} onOpenChange={(open) => !open && setDeletingProductId(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Xóa sản phẩm?</AlertDialogTitle>
            <AlertDialogDescription>
              Bạn có chắc chắn muốn xóa sản phẩm này? Hành động này không thể hoàn tác.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Hủy</AlertDialogCancel>
            <AlertDialogAction onClick={() => deletingProductId && handleDeleteProduct(deletingProductId)}>
              Xóa
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
