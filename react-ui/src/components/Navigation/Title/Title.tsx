import { Link } from "react-router-dom";

export default function Title() {
    return (
        <Link className="title-nav" to="/">
            <h1>Веб-приложение</h1>
        </Link>
    );
}