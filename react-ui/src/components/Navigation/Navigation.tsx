import "./Navigation.css";
import User from "../../UserInterface";
import Button from "./Button/Button";
import ActiveButton from "./ActiveButton/ActiveButton";
import Title from "./Title/Title";

interface NavigationProps {
    user: User | null;
}

export default function Navigation({ user }: NavigationProps) {
    return (
        <header>
            <nav>
                <Title />

                <div className="nav-links">
                    <ActiveButton name="Удалить визуальный шум" link="/" className="nav-link" />
                    <ActiveButton name="О системе" link="/about" className="nav-link" />
                </div>

                <div className="buttons">
                    {user ? (
                        <>
                            <span className="username">{user.username}</span>
                            <Button name="История" link="/history" className="login" />
                            <Button name="Выйти" link="/logout" className="register" />
                        </>
                    ) : (
                        <>
                            <Button name="Вход" link="/login" className="login" />
                            <Button name="Регистрация" link="/register" className="register" />
                        </>
                    )}
                </div>
            </nav>
        </header>
    );
}