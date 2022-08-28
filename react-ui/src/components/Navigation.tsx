import { Link } from "react-router-dom";
import { IUser } from "../App"
import "./Navigation.css"

interface INavProps {
    user: IUser | null;
};

export const Navigation = ({ user }: INavProps) => {
    return (
        <header>
            <nav>
                <a className="title-nav" href="/">
                    <h1>Веб-приложение</h1>
                </a>
                <div className="nav-links">
                    <Link className="link" to="/">
                        <div className="nav-link-button active">Удалить визуальный шум</div>
                    </Link>
                    <Link className="link" to="/about">
                        <div className="nav-link-button">О системе</div>
                    </Link>
                </div>
                <div className="buttons">
                    {user ? (
                        <>
                            <span className="username">{user.username}</span>
                            <Link className="link" to="/history">
                                <div className="login-button">История</div>
                            </Link>
                            <a className="link" href="/logout">
                                <div className="register-button">Выйти</div>
                            </a>
                        </>
                    ) : (
                        <>
                            <Link className="link" to="/login">
                                <div className="login-button">Вход</div>
                            </Link>
                            <Link className="link" to="/register">
                                <div className="register-button">Регистрация</div>
                            </Link>
                        </>
                    )}
                </div>
            </nav>
        </header>
    );
}