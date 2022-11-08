import ButtonProps from "../Button/ButtonPropsInterface";
import Button from "../Button/Button"

interface ActiveButtonProps extends ButtonProps{
    active: boolean
}

export default function ActiveButton({ active, className, ...props }: ActiveButtonProps) {
    const newClassName = active ? className + " active" : className;

    return (
        <Button className={newClassName} {...props} />
    );
}