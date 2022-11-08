import "./Navigation.css"
import User from "../../UserInterface"
import Button from "./Button/Button"
import ActiveButton from "./ActiveButton/ActiveButton";
import Title from "./Title/Title"

interface NavigationProps {
    user: User | null
}

export default function Navigation({ user }: NavigationProps) {
    return (
        <header>
            <nav>
                <Title />

                <div className="nav-links">
                    <ActiveButton active={true} name="Удалить визуальный шум" link="/" className="nav-link-button" />
                    <Button name="О системе" link="/about" className="nav-link-button" />
                </div>

                <div className="buttons">
                    {user ? (
                        <>
                            <span className="username">{user.username}</span>
                            <Button name="История" link="/history" className="login-button" />
                            <Button name="Выйти" link="/logout" className="register-button" />
                        </>
                    ) : (
                        <>
                            <Button name="Вход" link="/login" className="login-button" />
                            <Button name="Регистрация" link="/register" className="register-button" />
                        </>
                    )}
                </div>
            </nav>
        </header>
    );
}