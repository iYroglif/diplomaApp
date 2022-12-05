import { Link } from "react-router-dom";
import "./UserNavLink.css";

interface UserNavLinkProps {
  name: string;
  link: string;
  className: string;
}

export const UserNavLink = ({ name, link, className }: UserNavLinkProps) => {
  return (
    <Link className={`link ${className}`} to={link}>
      {name}
    </Link>
  );
};
