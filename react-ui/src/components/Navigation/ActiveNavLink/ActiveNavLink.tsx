import { NavLink } from "react-router-dom";
import "./ActiveNavLink.css";

interface ActiveNavLinkProps {
  name: string;
  link: string;
}

export const ActiveNavLink = ({ name, link }: ActiveNavLinkProps) => {
  return (
    <NavLink className={({ isActive }) => `link nav-link ${isActive ? "active" : ""}`} to={link}>
      {name}
    </NavLink>
  );
};
