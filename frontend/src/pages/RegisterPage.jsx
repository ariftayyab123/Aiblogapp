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
      heroTitle="Start Writing Smarter with AI"
      heroDescription="Generate authentic, engaging blog posts with AI-powered writing. Choose your style, enter a topic, and let AI do the rest."
      featurePoints={[
        'Create and own your private blog workspace',
        'Share public links and track real reader feedback',
      ]}
      formTitle="Create your account"
      formDescription="Sign up to generate blogs, share links, and track analytics."
      footer={(
        <>
          Already have an account?{' '}
          <Link to="/login" className="text-primary-300 hover:text-primary-200 hover:underline">
            Login
          </Link>
        </>
      )}
    >
      <form onSubmit={onSubmit} className="mt-8 space-y-5">
        <div>
          <label className="block text-sm font-semibold text-primary-100 mb-2">Email address</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="email"
            placeholder="you@example.com"
            className="w-full rounded-2xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder:text-primary-100/50 focus:outline-none focus:ring-2 focus:ring-primary-300"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-primary-100 mb-2">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="new-password"
            placeholder="Create a strong password"
            className="w-full rounded-2xl border border-white/20 bg-white/10 px-4 py-3 text-white placeholder:text-primary-100/50 focus:outline-none focus:ring-2 focus:ring-primary-300"
          />
        </div>

        <div>
          <label className="block text-sm font-semibold text-primary-100 mb-2">Confirm password</label>
          <input
            type="password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            autoComplete="new-password"
            placeholder="Re-enter your password"
            className={`w-full rounded-2xl border bg-white/10 px-4 py-3 text-white placeholder:text-primary-100/50 focus:outline-none focus:ring-2 ${
              mismatchError
                ? 'border-red-400 focus:ring-red-400'
                : 'border-white/20 focus:ring-primary-300'
            }`}
          />
          {mismatchError && <p className="mt-2 text-sm text-red-300">{mismatchError}</p>}
        </div>

        <Button
          type="submit"
          isLoading={isSubmitting}
          disabled={Boolean(mismatchError)}
          className="w-full rounded-2xl py-3 text-lg"
        >
          Sign up
        </Button>
      </form>
    </AuthLayout>
  );
}
