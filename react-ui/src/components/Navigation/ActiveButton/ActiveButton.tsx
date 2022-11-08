import Button from "../Button/Button"

interface ActiveButtonProps {
    active: boolean,

    name: string,
    link: string,
    className: string
}

export default function ActiveButton({ active, className, ...props }: ActiveButtonProps) {
    const newClassName = active ? className + " active" : className;

    return (
        <Button className={newClassName} {...props} />
    );
}