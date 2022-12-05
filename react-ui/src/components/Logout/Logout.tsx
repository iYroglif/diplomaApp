import { useNavigate } from "react-router-dom";
import { logoutURL } from "../../api/urls";
import "./Logout.css";

interface LogoutProps {
  setUser: (user: undefined) => void;
}

export const Logout = ({ setUser }: LogoutProps) => {
  const navigate = useNavigate();

  const logout = async () => {
    const response = await fetch(logoutURL);

    if (response.ok) {
      setUser(undefined);
      navigate("/");
    }
  };

  logout();

  return <div className="logout">Производится выход...</div>;
};
