import { useNavigate } from "react-router-dom";
import "./Logout.css";

interface LogoutProps {
    setUser: (user: null) => void;
}

export default function Logout({ setUser }: LogoutProps) {
    const navigate = useNavigate();

    const logout = async () => {
        const response = await fetch('/api/logout');

        if (response.ok) {
            setUser(null);
            navigate(-1);
        }
    };

    logout();

    return (
        <div className="logout">Производится выход...</div>
    );
}