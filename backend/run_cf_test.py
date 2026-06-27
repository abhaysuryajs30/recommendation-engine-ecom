from backend.models.collaborative import CollaborativeFilter

cf = CollaborativeFilter()
try:
    cf.load_data()
    cf.build_matrix()
    cf.compute_similarity()
    print("SMOKE OK")
except Exception as e:
    import traceback
    traceback.print_exc()
    print('ERROR:', type(e).__name__, e)
