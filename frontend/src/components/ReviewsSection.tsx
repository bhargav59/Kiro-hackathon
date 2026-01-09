import React, { useState, useEffect } from 'react';
import { Star, MessageCircle, ThumbsUp, Calendar, User } from 'lucide-react';

import { API_BASE } from '../config';

interface Review {
  id: number;
  user_id: number;
  tool_id: number;
  rating: number;
  title: string;
  content: string;
  pros: string[];
  cons: string[];
  use_case: string;
  experience_level: string;
  created_at: string;
  user?: {
    id: number;
    username: string;
    email: string;
  };
}

interface ReviewsProps {
  toolId: number;
  toolName: string;
}

const ReviewsSection: React.FC<ReviewsProps> = ({ toolId, toolName }) => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [newReview, setNewReview] = useState({
    rating: 5,
    title: '',
    content: '',
    pros: [''],
    cons: [''],
    use_case: '',
    experience_level: 'intermediate'
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReviews();
  }, [toolId]);

  const fetchReviews = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/tools/${toolId}/reviews`);
      if (response.ok) {
        const data = await response.json();
        setReviews(data);
      }
    } catch (error) {
      console.error('Error fetching reviews:', error);
    } finally {
      setLoading(false);
    }
  };

  const submitReview = async () => {
    try {
      const reviewData = {
        ...newReview,
        pros: newReview.pros.filter(pro => pro.trim()),
        cons: newReview.cons.filter(con => con.trim())
      };

      const response = await fetch(`${API_BASE}/api/tools/${toolId}/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // Add auth header when user system is implemented
        },
        body: JSON.stringify(reviewData)
      });

      if (response.ok) {
        fetchReviews();
        setShowReviewForm(false);
        setNewReview({
          rating: 5,
          title: '',
          content: '',
          pros: [''],
          cons: [''],
          use_case: '',
          experience_level: 'intermediate'
        });
      }
    } catch (error) {
      console.error('Error submitting review:', error);
    }
  };

  const addProsCons = (type: 'pros' | 'cons') => {
    setNewReview(prev => ({
      ...prev,
      [type]: [...prev[type], '']
    }));
  };

  const updateProsCons = (type: 'pros' | 'cons', index: number, value: string) => {
    setNewReview(prev => ({
      ...prev,
      [type]: prev[type].map((item, i) => i === index ? value : item)
    }));
  };

  const removeProsCons = (type: 'pros' | 'cons', index: number) => {
    setNewReview(prev => ({
      ...prev,
      [type]: prev[type].filter((_, i) => i !== index)
    }));
  };

  const renderStars = (rating: number, interactive = false, onRatingChange?: (rating: number) => void) => {
    return (
      <div className="flex space-x-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            size={20}
            className={`${
              star <= rating 
                ? 'text-yellow-500 fill-current' 
                : 'text-gray-300'
            } ${interactive ? 'cursor-pointer hover:text-yellow-400' : ''}`}
            onClick={() => interactive && onRatingChange && onRatingChange(star)}
          />
        ))}
      </div>
    );
  };

  const averageRating = reviews.length > 0 
    ? reviews.reduce((sum, review) => sum + review.rating, 0) / reviews.length 
    : 0;

  if (loading) {
    return (
      <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/4"></div>
          <div className="space-y-3">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-10">
      {/* Reviews Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            💬 User Reviews
          </h2>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              {renderStars(Math.round(averageRating))}
              <span className="text-lg font-semibold text-gray-700">
                {averageRating.toFixed(1)} out of 5
              </span>
            </div>
            <span className="text-gray-500">
              ({reviews.length} {reviews.length === 1 ? 'review' : 'reviews'})
            </span>
          </div>
        </div>
        <button
          onClick={() => setShowReviewForm(!showReviewForm)}
          className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
        >
          Write Review
        </button>
      </div>

      {/* Review Form */}
      {showReviewForm && (
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-8 mb-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Write a Review for {toolName}</h3>
          
          <div className="space-y-6">
            {/* Rating */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Rating</label>
              {renderStars(newReview.rating, true, (rating) => 
                setNewReview(prev => ({ ...prev, rating }))
              )}
            </div>

            {/* Title */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Review Title</label>
              <input
                type="text"
                value={newReview.title}
                onChange={(e) => setNewReview(prev => ({ ...prev, title: e.target.value }))}
                placeholder="Summarize your experience..."
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Content */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Detailed Review</label>
              <textarea
                value={newReview.content}
                onChange={(e) => setNewReview(prev => ({ ...prev, content: e.target.value }))}
                placeholder="Share your detailed experience with this tool..."
                rows={4}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Pros */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Pros</label>
              {newReview.pros.map((pro, index) => (
                <div key={index} className="flex space-x-2 mb-2">
                  <input
                    type="text"
                    value={pro}
                    onChange={(e) => updateProsCons('pros', index, e.target.value)}
                    placeholder="What did you like about this tool?"
                    className="flex-1 px-4 py-2 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  />
                  {newReview.pros.length > 1 && (
                    <button
                      onClick={() => removeProsCons('pros', index)}
                      className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={() => addProsCons('pros')}
                className="text-green-600 hover:text-green-700 font-medium"
              >
                + Add another pro
              </button>
            </div>

            {/* Cons */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Cons</label>
              {newReview.cons.map((con, index) => (
                <div key={index} className="flex space-x-2 mb-2">
                  <input
                    type="text"
                    value={con}
                    onChange={(e) => updateProsCons('cons', index, e.target.value)}
                    placeholder="What could be improved?"
                    className="flex-1 px-4 py-2 border-2 border-gray-200 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
                  />
                  {newReview.cons.length > 1 && (
                    <button
                      onClick={() => removeProsCons('cons', index)}
                      className="px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                    >
                      ✕
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={() => addProsCons('cons')}
                className="text-red-600 hover:text-red-700 font-medium"
              >
                + Add another con
              </button>
            </div>

            {/* Use Case */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Use Case</label>
              <input
                type="text"
                value={newReview.use_case}
                onChange={(e) => setNewReview(prev => ({ ...prev, use_case: e.target.value }))}
                placeholder="How did you use this tool? (e.g., CI/CD, monitoring, etc.)"
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Experience Level */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Experience Level</label>
              <select
                value={newReview.experience_level}
                onChange={(e) => setNewReview(prev => ({ ...prev, experience_level: e.target.value }))}
                className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
                <option value="expert">Expert</option>
              </select>
            </div>

            {/* Submit Buttons */}
            <div className="flex space-x-4">
              <button
                onClick={submitReview}
                className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-xl font-semibold hover:from-green-700 hover:to-emerald-700 transition-all duration-200"
              >
                Submit Review
              </button>
              <button
                onClick={() => setShowReviewForm(false)}
                className="bg-gray-500 text-white px-6 py-3 rounded-xl font-semibold hover:bg-gray-600 transition-all duration-200"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Reviews List */}
      <div className="space-y-6">
        {reviews.length === 0 ? (
          <div className="text-center py-12">
            <MessageCircle size={48} className="text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-600 mb-2">No reviews yet</h3>
            <p className="text-gray-500">Be the first to review {toolName}!</p>
          </div>
        ) : (
          reviews.map((review) => (
            <div key={review.id} className="border-2 border-gray-100 rounded-xl p-6 hover:border-blue-200 transition-all duration-200">
              {/* Review Header */}
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center space-x-3 mb-2">
                    {renderStars(review.rating)}
                    <span className="font-semibold text-gray-900">{review.title}</span>
                  </div>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <div className="flex items-center space-x-1">
                      <User size={16} />
                      <span>Anonymous User</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Calendar size={16} />
                      <span>{new Date(review.created_at).toLocaleDateString()}</span>
                    </div>
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-lg">
                      {review.experience_level}
                    </span>
                  </div>
                </div>
              </div>

              {/* Review Content */}
              <p className="text-gray-700 leading-relaxed mb-4">{review.content}</p>

              {/* Use Case */}
              {review.use_case && (
                <div className="mb-4">
                  <span className="font-semibold text-gray-700">Use Case: </span>
                  <span className="text-gray-600">{review.use_case}</span>
                </div>
              )}

              {/* Pros and Cons */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {review.pros && review.pros.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-green-800 mb-2 flex items-center">
                      <span className="text-green-500 mr-2">✓</span> Pros
                    </h4>
                    <ul className="space-y-1">
                      {review.pros.map((pro, index) => (
                        <li key={index} className="text-green-700 text-sm">• {pro}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {review.cons && review.cons.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-red-800 mb-2 flex items-center">
                      <span className="text-red-500 mr-2">✗</span> Cons
                    </h4>
                    <ul className="space-y-1">
                      {review.cons.map((con, index) => (
                        <li key={index} className="text-red-700 text-sm">• {con}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ReviewsSection;
