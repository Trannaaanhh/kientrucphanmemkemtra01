import { useState } from "react";
import { useNavigate, Link } from "react-router";
import { ShoppingCart, Mail, Lock, ArrowLeft } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Button } from "../components/ui/button";
import { Label } from "../components/ui/label";
import { apiRequest, saveAuthToken, saveUserInfo } from "../services/api";

export function CustomerLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("customer@example.com");
  const [password, setPassword] = useState("customer123");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      const data = await apiRequest<{ access_token: string; role: "customer"; name?: string; email?: string }>("/auth/customer/login", {
        method: "POST",
        body: { email, password },
      });
      saveAuthToken(data.access_token, data.role);
      saveUserInfo(data.role, data.name ?? "", data.email ?? email);
      navigate("/customer/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Đăng nhập thất bại");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <Link to="/" className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-6">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Quay lại
        </Link>

        <Card>
          <CardHeader className="text-center">
            <div className="mx-auto w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center mb-4">
              <ShoppingCart className="w-8 h-8 text-white" />
            </div>
            <CardTitle className="text-3xl">Đăng Nhập Khách Hàng</CardTitle>
            <CardDescription>
              Đăng nhập để mua sắm sản phẩm
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleLogin} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="customer@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Mật khẩu</Label>
                <div className="relative">
                  <Lock className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="pl-10"
                    required
                  />
                </div>
              </div>

              <Button type="submit" className="w-full" size="lg">
                {isLoading ? "Đang đăng nhập..." : "Đăng Nhập"}
              </Button>

              {error && <p className="text-sm text-red-600">{error}</p>}

              <div className="text-center text-sm text-gray-600">
                Chưa có tài khoản?{" "}
                <a href="#" className="text-blue-600 hover:underline">
                  Đăng ký ngay
                </a>
              </div>
            </form>
          </CardContent>
        </Card>

        <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <p className="text-sm text-blue-800">
            <strong>Demo:</strong> customer@example.com / customer123
          </p>
        </div>
      </div>
    </div>
  );
}
