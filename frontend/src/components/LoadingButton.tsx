import { useState } from 'react';

interface LoadingButtonProps {
  buttonClickFunction: () => void | Promise<void>;
  buttonText: string;
  styles?: string;
  disabled?: boolean;
}

export const LoadingButton = ({
  buttonClickFunction,
  buttonText,
  disabled = false,
  styles = 'bg-yellow-400 hover:bg-yellow-300 text-gray-900'
}: LoadingButtonProps) => {
  const [loading, setLoading] = useState<boolean>(false);

  const onClick = async () => {
    setLoading(true);

    try {
      await buttonClickFunction();
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      onClick={onClick}
      disabled={loading || disabled}
      className={`${styles} font-bold tracking-wider transition-colors flex items-center justify-center`}
    >
      {loading ? (
        <div className="animate-spin rounded-full h-4 w-4 border-2 border-current border-t-transparent" />
      ) : (
        buttonText
      )}
    </button>
  );
};
