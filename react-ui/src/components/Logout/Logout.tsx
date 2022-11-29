import { useNavigate } from "react-router-dom";
import "./Logout.css";

interface LogoutProps {
  setUser: (user: undefined) => void;
}

export default function Logout({ setUser }: LogoutProps) {
  const navigate = useNavigate();

  const logout = async () => {
    const logoutUrl = "/api/logout";
    const response = await fetch(logoutUrl);

    if (response.ok) {
      setUser(undefined);
      navigate("/");
    }
  };

  logout();

  return <div className="logout">Производится выход...</div>;
}
