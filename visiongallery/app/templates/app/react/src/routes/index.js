import Home from "../pages/home";
import login from "../pages/login/login";
import register from "../pages/register/register";
import privacy from "../pages/privacy/privacy";
export const routes = [
  {
    path: "/home",
    component: Home,
  },
  {
    path: "/login",
    component: login,
  },
  {
    path: "/register",
    component: register,
  },
  {
    path: "/privacy",
    component: privacy,
  },

];
