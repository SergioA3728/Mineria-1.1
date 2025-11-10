
# Dashboard - Universidad (Entregable)

Este paquete contiene una aplicación Streamlit lista para ejecutar, junto con documentación y recomendaciones de seguridad.

## Contenido del ZIP
- app.py
- requirements.txt
- README.md
- university_student_data.csv 
- deploy_instructions.sh 

## Instrucciones rápidas

### Ejecutar localmente
1. Crear entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   pip install -r requirements.txt
   ```
2. Coloca `university_student_data.csv` en el mismo directorio.
3. Ejecuta:
   ```bash
   streamlit run app.py
   ```
4. Abre `http://localhost:8501`.
   ```

## Checklist y buenas prácticas (ingeniería)
- [ ] Validar que no haya datos personales (PII) en CSV si el repositorio será público.
- [ ] Usar `st.cache_data` para operaciones de carga/transformación.
- [ ] No incluir secretos en el código.
- [ ] Mantener `requirements.txt` actualizado y fijar versiones si es necesario.
- [ ] Añadir pruebas unitarias simples para transformaciones críticas (opcional).


