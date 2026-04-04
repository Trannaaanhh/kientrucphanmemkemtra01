import { Link } from "react-router";
import { ShoppingCart, UserCog } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";

export function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Hệ Thống Kiểm Tra 01
          </h1>
          <p className="text-xl text-gray-600">
            Quản lý sản phẩm Laptop & Mobile
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Customer Card */}
          <Card className="hover:shadow-xl transition-shadow">
            <CardHeader className="text-center">
              <div className="mx-auto w-20 h-20 bg-blue-500 rounded-full flex items-center justify-center mb-4">
                <ShoppingCart className="w-10 h-10 text-white" />
              </div>
              <CardTitle className="text-2xl">Khách Hàng</CardTitle>
              <CardDescription>
                Tìm kiếm và mua sắm sản phẩm
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link to="/customer/login">
                <Button className="w-full" size="lg">
                  Đăng Nhập Khách Hàng
                </Button>
              </Link>
              <ul className="mt-4 space-y-2 text-sm text-gray-600">
                <li>• Tìm kiếm sản phẩm</li>
                <li>• Thêm vào giỏ hàng</li>
                <li>• Quản lý đơn hàng</li>
              </ul>
            </CardContent>
          </Card>

          {/* Staff Card */}
          <Card className="hover:shadow-xl transition-shadow">
            <CardHeader className="text-center">
              <div className="mx-auto w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mb-4">
                <UserCog className="w-10 h-10 text-white" />
              </div>
              <CardTitle className="text-2xl">Nhân Viên</CardTitle>
              <CardDescription>
                Quản lý kho hàng và sản phẩm
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link to="/staff/login">
                <Button className="w-full" variant="outline" size="lg">
                  Đăng Nhập Nhân Viên
                </Button>
              </Link>
              <ul className="mt-4 space-y-2 text-sm text-gray-600">
                <li>• Thêm mặt hàng mới</li>
                <li>• Cập nhật sản phẩm</li>
                <li>• Quản lý kho hàng</li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
