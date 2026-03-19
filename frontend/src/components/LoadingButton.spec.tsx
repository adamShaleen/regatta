import userEvent from '@testing-library/user-event';
import { render, screen, waitFor } from '@testing-library/react';
import { LoadingButton } from './LoadingButton';

describe('LoadingButton', () => {
  const setup = (
    buttonClickFunction = vi.fn(),
    buttonText = 'mock button text'
  ) => {
    const user = userEvent.setup();

    render(
      <LoadingButton
        buttonText={buttonText}
        buttonClickFunction={buttonClickFunction}
      />
    );

    return {
      user,
      button: screen.getByRole('button'),
      buttonClickFunction
    };
  };

  it('button text', () => {
    const { button } = setup();
    expect(button).toHaveTextContent('mock button text');
  });

  it('onClick calls button function', async () => {
    const mockButtonClickFunction = vi.fn();

    const { user, button } = setup(mockButtonClickFunction);
    await user.click(button);

    expect(mockButtonClickFunction).toHaveBeenCalledTimes(1);
  });

  it('button is disabled while loading', async () => {
    let resolve!: () => void;
    
    const slowFunction = vi.fn(
      () =>
        new Promise<void>((res) => {
          resolve = res;
        })
    );

    const { user, button } = setup(slowFunction);
    const clickPromise = user.click(button);

    await waitFor(() => expect(button).toBeDisabled());

    resolve();
    await clickPromise;

    expect(button).not.toBeDisabled();
  });
});
