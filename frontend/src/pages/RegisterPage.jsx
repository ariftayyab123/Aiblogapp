import { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { useToast } from '../contexts/ToastContext';
import { useAuth } from '../contexts/AuthContext';
import AuthLayout from '../components/layout/AuthLayout';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { error, success } = useToast();
  const { register } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const mismatchError = useMemo(() => {
    if (!confirmPassword) return '';
    return password === confirmPassword ? '' : 'Passwords do not match';
  }, [password, confirmPassword]);

  const onSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting || mismatchError) return;
    setIsSubmitting(true);
    try {
      await register(email, password, confirmPassword);
      success('Registration successful');
      navigate('/');
    } catch (err) {
      error(err?.message || 'Registration failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <AuthLayout
      heroTitle="Start a writing workspace"
      heroDescription="Create an account to draft posts with their sources attached, keep them private while you edit, and publish share links when they're ready."
      featurePoints={[
        'Your workspace is yours alone — every post is scoped to your account.',
        'Share a public link when a draft is ready, then track how it lands.',
      ]}
      formTitle="Create account"
      formDescription="Choose an email and a password. That is all you need."
      footer={(
        <>
          Already have an account?{' '}
          <Link to="/login" className="link-editorial">
            Sign in
          </Link>
        </>
      )}
    >
      <form onSubmit={onSubmit} className="mt-8 space-y-5">
        <div>
          <label htmlFor="register-email" className="field-label">
            Email address
          </label>
          <input
            id="register-email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
            placeholder="you@example.com"
            className="input-editorial"
          />
        </div>

        <div>
          <label htmlFor="register-password" className="field-label">
            Password
          </label>
          <input
            id="register-password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="new-password"
            placeholder="Create a strong password"
            className="input-editorial"
          />
        </div>

        <div>
          <label htmlFor="register-confirm" className="field-label">
            Confirm password
          </label>
          <input
            id="register-confirm"
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            autoComplete="new-password"
            placeholder="Re-enter your password"
            aria-invalid={Boolean(mismatchError) || undefined}
            aria-describedby={mismatchError ? 'register-confirm-error' : undefined}
            className={`input-editorial ${
              mismatchError ? 'border-red-500 focus:border-red-500 dark:border-red-500' : ''
            }`}
          />
          {mismatchError && (
            <p id="register-confirm-error" className="mt-2 text-sm text-red-600 dark:text-red-400">
              {mismatchError}
            </p>
          )}
        </div>

        <Button
          type="submit"
          variant="ink"
          isLoading={isSubmitting}
          disabled={Boolean(mismatchError)}
          className="w-full justify-center py-3"
        >
          Sign up
        </Button>
      </form>
    </AuthLayout>
  );
}
