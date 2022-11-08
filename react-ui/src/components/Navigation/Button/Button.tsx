import { Link } from "react-router-dom";

interface ButtonProps {
    name: string,
    link: string,
    className: string
}

export default function Button({ name, link, className }: ButtonProps) {
    return (
        <Link className="link" to={link}>
            <div className={className}>{name}</div>
        </Link>
    );
}