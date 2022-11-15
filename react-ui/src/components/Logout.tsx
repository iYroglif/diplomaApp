import { useNavigate } from "react-router-dom";

export default function Logout() {
    const navigate = useNavigate();

    const logout = async () => {
        const response = await fetch('/api/logout');

        if (response.ok) {
            navigate(-1);
        }
    };

    logout();

    return (
        <p>Производится выход...</p>
    );
}