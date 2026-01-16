#!/usr/bin/env python3
"""
Update Firestore Security Rules to allow read access to daily_rankings collection
"""

import firebase_admin
from firebase_admin import credentials, firestore
import json

def update_firestore_rules():
    """Update Firestore security rules"""
    
    # Initialize Firebase Admin SDK
    cred = credentials.Certificate('serviceAccountKey.json')
    
    try:
        firebase_admin.get_app()
    except ValueError:
        firebase_admin.initialize_app(cred)
    
    print("✅ Firebase Admin initialized")
    
    # Note: The Firebase Admin SDK doesn't support updating security rules directly
    # Rules must be updated through:
    # 1. Firebase Console: https://console.firebase.google.com/project/k-rank-c5bad/firestore/rules
    # 2. Firebase CLI: firebase deploy --only firestore:rules
    
    print("\n⚠️  Security rules cannot be updated via Admin SDK.")
    print("\nPlease update Firestore Security Rules manually:")
    print("1. Visit: https://console.firebase.google.com/project/k-rank-c5bad/firestore/rules")
    print("2. Replace the rules with the following:\n")
    
    rules = """rules_version = '2';

service cloud.firestore {
  match /databases/{database}/documents {
    // Allow read access to daily_rankings for everyone
    match /daily_rankings/{document=**} {
      allow read: if true;
      allow write: if false; // Only server can write
    }
    
    // Deny all other access by default
    match /{document=**} {
      allow read, write: if false;
    }
  }
}"""
    
    print(rules)
    print("\n3. Click 'Publish' to apply the rules")
    print("\n📋 The rules have also been saved to: firestore.rules\n")

if __name__ == "__main__":
    update_firestore_rules()
