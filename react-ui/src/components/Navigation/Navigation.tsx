import "./Navigation.css";
import { User } from "../../UserInterface";
import { UserNavLink } from "./UserNavLink/UserNavLink";
import { ActiveNavLink } from "./ActiveNavLink/ActiveNavLink";
import { Title } from "./Title/Title";

interface NavigationProps {
  user?: User;
}

export const Navigation = ({ user }: NavigationProps) => {
  return (
    <header>
      <nav>
        <Title />

        <div className="nav-links">
          <ActiveNavLink name="Удалить визуальный шум" link="/" />
          <ActiveNavLink name="О системе" link="/about" />
        </div>

        <div className="nav-buttons">
          {user ? (
            <>
              <span className="username">{user.username}</span>
              <UserNavLink name="История" link="/history" className="login" />
              <UserNavLink name="Выйти" link="/logout" className="register" />
            </>
          ) : (
            <>
              <UserNavLink name="Вход" link="/login" className="login" />
              <UserNavLink name="Регистрация" link="/register" className="register" />
            </>
          )}
        </div>
      </nav>
    </header>
  );
};
