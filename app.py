from flask import Flask, request, jsonify
from flask_cors import CORS
import fdb
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

# Firebird database configuration
FIREBIRD_CONFIG = {
    'host': os.getenv('FIREBIRD_HOST', 'localhost'),
    'port': int(os.getenv('FIREBIRD_PORT', 3050)),
    'database': os.getenv('FIREBIRD_DATABASE_PATH', ''),
    'user': os.getenv('FIREBIRD_USER', 'sysdba'),
    'password': os.getenv('FIREBIRD_PASSWORD', 'masterkey'),
    'charset': os.getenv('FIREBIRD_CHARSET', 'WIN1254'),
    'pageSize': int(os.getenv('FIREBIRD_PAGE_SIZE', 4096))
}


def get_db_connection():
    """Create and return a Firebird database connection"""
    try:
        conn = fdb.connect(
            host=FIREBIRD_CONFIG['host'],
            port=FIREBIRD_CONFIG['port'],
            database=FIREBIRD_CONFIG['database'],
            user=FIREBIRD_CONFIG['user'],
            password=FIREBIRD_CONFIG['password'],
            charset=FIREBIRD_CONFIG.get('charset', 'WIN1254')
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise e


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'healthy', 'database_configured': True})
    except Exception as e:
        return jsonify({'status': 'healthy', 'database_configured': False, 'error': str(e)})


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current database configuration (without password)"""
    return jsonify({
        'host': FIREBIRD_CONFIG['host'],
        'port': FIREBIRD_CONFIG['port'],
        'database': FIREBIRD_CONFIG['database'],
        'user': FIREBIRD_CONFIG['user']
    })


@app.route('/api/config', methods=['POST'])
def update_config():
    """Update database configuration"""
    data = request.json
    
    required_fields = ['host', 'database', 'user', 'password']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    FIREBIRD_CONFIG['host'] = data['host']
    FIREBIRD_CONFIG['port'] = int(data.get('port', 3050))
    FIREBIRD_CONFIG['database'] = data['database']
    FIREBIRD_CONFIG['user'] = data['user']
    FIREBIRD_CONFIG['password'] = data['password']
    
    return jsonify({'message': 'Configuration updated successfully'})


@app.route('/api/test-connection', methods=['POST'])
def test_connection():
    """Test database connection with provided credentials"""
    data = request.json

    try:
        conn = fdb.connect(
            host=data.get('host', FIREBIRD_CONFIG['host']),
            port=int(data.get('port', FIREBIRD_CONFIG['port'])),
            database=data.get('database', FIREBIRD_CONFIG['database']),
            user=data.get('user', FIREBIRD_CONFIG['user']),
            password=data.get('password', FIREBIRD_CONFIG['password']),
            charset=data.get('charset', FIREBIRD_CONFIG.get('charset', 'WIN1254'))
        )
        conn.close()
        return jsonify({'success': True, 'message': 'Connection successful'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/barcode', methods=['POST'])
def get_product_by_barcode():
    """Get product information by barcode"""
    try:
        data = request.json
        barcode = data.get('barcode')

        # Get connection parameters from request
        host = data.get('host', FIREBIRD_CONFIG['host'])
        port = data.get('port', FIREBIRD_CONFIG['port'])
        database = data.get('database', FIREBIRD_CONFIG['database'])
        user = data.get('user', FIREBIRD_CONFIG['user'])
        password = data.get('password', FIREBIRD_CONFIG['password'])
        charset = data.get('charset', FIREBIRD_CONFIG.get('charset', 'WIN1254'))

        # Clean barcode - remove whitespace and hidden characters
        barcode = barcode.strip()
        barcode = barcode.replace('\n', '').replace('\r', '').replace('\t', '')

        conn = fdb.connect(
            host=host,
            port=int(port),
            database=database,
            user=user,
            password=password,
            charset=charset
        )
        cursor = conn.cursor()

        # Custom query based on user requirements
        query = f"""
        SELECT s.blkodu as indexno, s.stokkodu as stokkodu, s.stok_adi as stokadi, sf.fiyati as fiyati, s.barkodu as barkodu
        FROM STOK as s, stok_fiyat as sf
        WHERE s.blkodu = sf.blstkodu
        AND sf.alis_satis = 2
        AND sf.fiyat_no = 1
        AND s.barkodu = '{barcode}'
        """

        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            # Convert result to dictionary
            columns = ['indexno', 'stokkodu', 'stokadi', 'fiyati', 'barkodu']
            product_dict = dict(zip(columns, result))
            return jsonify({'success': True, 'product': product_dict})
        else:
            return jsonify({'success': False, 'message': 'Stok Bulunamadı...!'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/barcode', methods=['POST'])
def create_or_update_product():
    """Create or update product by barcode"""
    data = request.json
    barcode = data.get('barcode')
    
    if not barcode:
        return jsonify({'error': 'Barcode is required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if product exists
        check_query = "SELECT ID FROM PRODUCTS WHERE BARCODE = ?"
        cursor.execute(check_query, (barcode,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing product
            update_query = """
            UPDATE PRODUCTS SET 
                NAME = ?, 
                PRICE = ?, 
                STOCK = ?,
                UPDATED_AT = CURRENT_TIMESTAMP
            WHERE BARCODE = ?
            """
            cursor.execute(update_query, (
                data.get('name'),
                data.get('price'),
                data.get('stock'),
                barcode
            ))
        else:
            # Insert new product
            insert_query = """
            INSERT INTO PRODUCTS (BARCODE, NAME, PRICE, STOCK, CREATED_AT)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """
            cursor.execute(insert_query, (
                barcode,
                data.get('name'),
                data.get('price'),
                data.get('stock')
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Product saved successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/query', methods=['POST'])
def execute_custom_query():
    """Execute custom SQL query (use with caution)"""
    data = request.json
    query = data.get('query')
    params = data.get('params', [])
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(query, tuple(params))
        
        if query.strip().upper().startswith('SELECT'):
            results = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            result_dicts = [dict(zip(columns, row)) for row in results]
            
            cursor.close()
            conn.close()
            
            return jsonify({'success': True, 'results': result_dicts})
        else:
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Query executed successfully'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('FLASK_PORT', 5000)), debug=True)
