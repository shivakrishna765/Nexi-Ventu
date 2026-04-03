import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ROLE_ROUTES = {
  investor:     "/investor-dashboard",
  founder:      "/founder-dashboard",
  seeker:       "/team-dashboard",
  member:       "/team-dashboard",
  collaborator: "/collaborator-dashboard",
};

/**
 * ProtectedRoute — blocks unauthenticated users and enforces role-based access.
 *
 * Props:
 *   allowedRoles  — array of roles that may access this route (omit = any auth user)
 *   adminOnly     — if true, only is_admin users may access
 */
export default function ProtectedRoute({ children, allowedRoles, adminOnly = false }) {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-violet-500 border-t-transparent" />
      </div>
    );
  }

  // Not logged in → send to login
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Admin-only route
  if (adminOnly && !user.is_admin) {
    return <Navigate to="/" replace />;
  }

  // Role-restricted route
  if (allowedRoles && allowedRoles.length > 0) {
    const normalised = (user.role || "member").toLowerCase();
    const effective  = normalised === "member" ? "seeker" : normalised;
    if (!allowedRoles.includes(effective)) {
      const redirect = ROLE_ROUTES[normalised] || "/team-dashboard";
      return <Navigate to={redirect} replace />;
    }
  }

  return children;
}
