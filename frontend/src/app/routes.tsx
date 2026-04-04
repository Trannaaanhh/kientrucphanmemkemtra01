import { createBrowserRouter } from "react-router";
import { HomePage } from "./pages/HomePage";
import { CustomerLogin } from "./pages/CustomerLogin";
import { StaffLogin } from "./pages/StaffLogin";
import { CustomerDashboard } from "./pages/CustomerDashboard";
import { StaffDashboard } from "./pages/StaffDashboard";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: HomePage,
  },
  {
    path: "/customer/login",
    Component: CustomerLogin,
  },
  {
    path: "/customer/dashboard",
    Component: CustomerDashboard,
  },
  {
    path: "/staff/login",
    Component: StaffLogin,
  },
  {
    path: "/staff/dashboard",
    Component: StaffDashboard,
  },
]);
